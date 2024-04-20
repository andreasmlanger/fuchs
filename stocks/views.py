import os
from bokeh.embed import file_html, components
from bokeh.resources import CDN
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Stock
from .plots import *
from .finance import *
from main.utils import get_avatar, update_notification
from main.emails import send_email


ETF = 'URTH'  # iShares MSCI World ETF
MIN = -15  # % down for notification
MAX = 5  # % up for notification


@login_required
def portfolio(request):
    # Upload stocks
    if request.FILES:
        upload_stocks(request.FILES.getlist('document')[0], request.user)

    # Download stocks
    if 'Content-Type' in request.headers and request.headers['Content-Type'] == 'application/json':
        return download_stocks(request.user)

    alert, message = 'success', 'Stocks are up-to-date!'  # refresh

    if request.POST.get('stock_to_remove'):
        remove_shares(request.user, request.POST.get('stock_to_remove'), int(request.POST.get('number')))
        message = 'Shares removed!'

    # Load stock data from Yahoo
    stocks = [s.symbol for s in request.user.stocks.filter(in_portfolio=True)] + [ETF]  # include MSCI World ETF
    first_order = min([s.order_date for s in request.user.stocks.filter(in_portfolio=True)] + [datetime.today()])

    df_yahoo = get_stock_data(stocks, request.POST.get('stock_to_add'), first_order, request.POST.get('order_date'))

    if request.POST.get('stock_to_add'):
        if request.POST.get('stock_to_add') in df_yahoo.columns:  # if successful, add stock to model
            Stock(in_portfolio=True,
                  user=request.user,
                  symbol=request.POST.get('stock_to_add'),
                  name=request.POST.get('name'),
                  order_date=datetime.strptime(request.POST.get('order_date'), '%b %d, %Y'),
                  order_price=request.POST.get('order_price'),
                  volume=request.POST.get('volume')
                  ).save()
            message = f'{request.POST.get("name")} was added to portfolio!'
        else:
            alert, message = 'danger', 'Error fetching stock!'

    # Load user portfolio
    pf, df, df2 = get_populated_portfolio(request.user, df_yahoo)

    # Return if empty portfolio
    if len(pf) == 0:
        return no_stocks_response(request, message, alert, 'stocks/portfolio.html')

    # Create Bokeh plots and table
    p1 = create_individual_portfolio_plot(df, pf)
    p2 = create_aggregated_portfolio_plot(df, df2)
    table = pf.to_json(orient='records')

    if request.method == 'POST':
        return JsonResponse({'bokeh': file_html(p1, CDN, 'bokeh'), 'bokeh2': file_html(p2, CDN, 'bokeh'),
                             'table': table, 'message': message, 'alert': alert})

    script, div = components(p1)
    script2, div2 = components(p2)

    return render(request, 'stocks/portfolio.html', {'script': script, 'div': div, 'script2': script2, 'div2': div2,
                                                     'table': table, 'avatar': get_avatar(request)})


@login_required
def watchlist(request):
    # Upload stocks
    if request.FILES:
        upload_stocks(request.FILES.getlist('document')[0], request.user, in_portfolio=False)

    # Download stocks
    if 'Content-Type' in request.headers and request.headers['Content-Type'] == 'application/json':
        return download_stocks(request.user, in_portfolio=False)

    alert, message = 'success', 'Stocks are up-to-date!'  # refresh

    if request.POST.get('stock_to_delete'):
        request.user.stocks.get(symbol=request.POST.get('stock_to_delete'), in_portfolio=False).delete()
        alert, message = 'success', 'Stock removed!'

    # Load stock data from Yahoo including MSCI World ETF
    stocks = [s.symbol for s in request.user.stocks.filter(in_portfolio=False)]

    # Get last 3 years of Yahoo data
    df_yahoo = get_stock_data(stocks, request.POST.get('stock_to_add'))

    if request.POST.get('stock_to_add'):
        if request.POST.get('stock_to_add') in df_yahoo.columns:  # if successful, add stock to model
            Stock(in_portfolio=False,
                  user=request.user,
                  symbol=request.POST.get('stock_to_add'),
                  name=request.POST.get('name')
                  ).save()
            message = f'{request.POST.get("name")} was added to watchlist!'

        elif request.POST.get('stock_to_add'):
            alert, message = 'danger', 'Error fetching stock!'

    # Load user watchlist
    pf, df, df_90, df_vo = get_populated_watchlist(request.user, df_yahoo)

    # Return if watchlist is empty
    if len(pf) == 0:
        return no_stocks_response(request, message, alert, 'stocks/watchlist.html')

    # Create Bokeh plots and table
    p = create_individual_watchlist_plot(df, pf, df_90)
    p2 = create_watchlist_volatility_plot(df_vo, pf)
    table = pf.to_json(orient='records')

    if request.method == 'POST':
        return JsonResponse({'bokeh': file_html(p, CDN, 'bokeh'), 'bokeh2': file_html(p2, CDN, 'bokeh'),
                             'table': table, 'message': message, 'alert': alert})

    script, div = components(p)
    script2, div2 = components(p2)

    return render(request, 'stocks/watchlist.html', {'script': script, 'div': div, 'script2': script2, 'div2': div2,
                                                     'table': table, 'avatar': get_avatar(request)})


def upload_stocks(f, user, in_portfolio=True):
    if in_portfolio:  # Portfolio
        df = pd.ExcelFile(f).parse('Portfolio')

        model_instances = [Stock(
            user=user,
            in_portfolio=in_portfolio,
            symbol=r['symbol'],
            name=r['name'],
            order_date=datetime.strptime(r['order_date'], '%Y-%m-%d'),
            order_price=r['order_price'],
            volume=r['volume'],
        ) for r in df.to_dict('records')]

    else:  # Watchlist
        df = pd.ExcelFile(f).parse('Watchlist')

        model_instances = [Stock(
            user=user,
            in_portfolio=in_portfolio,
            symbol=r['symbol'],
            name=r['name'],
        ) for r in df.to_dict('records')]

    Stock.objects.bulk_create(model_instances)


def download_stocks(user, in_portfolio=True):
    pf = load_user_portfolio(user, in_portfolio=in_portfolio)

    if in_portfolio:
        pf['order_date'] = pf['order_date'].dt.strftime('%Y-%m-%d')
        sheet_name = 'Portfolio'
    else:
        pf = pf[['symbol', 'name']]
        sheet_name = 'Watchlist'

    file_path = os.path.join(settings.MEDIA_ROOT, user.username + '_export.xlsx')

    with pd.ExcelWriter(file_path) as writer:
        pf.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        for idx, col in enumerate(pf):
            worksheet.set_column(idx, idx, 14)

    with open(file_path, 'rb') as fh:
        file_data = fh.read()

    os.remove(file_path)  # clean up
    return HttpResponse(file_data, content_type='application/ms-excel')


def load_user_portfolio(user, in_portfolio):
    stocks = user.stocks.filter(in_portfolio=in_portfolio)

    df = pd.DataFrame()
    df['symbol'] = [s.symbol for s in stocks]
    df['name'] = [s.name for s in stocks]
    df['order_date'] = [s.order_date.strftime('%Y-%m-%d') if s.order_date else None for s in stocks]
    df['volume'] = [s.volume for s in stocks]
    df['order_price'] = [s.order_price for s in stocks]
    df['investment'] = df['volume'] * df['order_price']

    df['order_date'] = pd.to_datetime(df['order_date'], format='%Y-%m-%d')

    return df.sort_values('name')


def get_populated_portfolio(user, df_yahoo):
    pf = load_user_portfolio(user, in_portfolio=True)

    if len(pf) == 0:  # if only ETF in
        return pf, pd.DataFrame(), pd.DataFrame()

    # Populate dataframe of stocks with Yahoo data keeping duplicates
    df = pd.DataFrame()
    for idx, stock in enumerate(pf['symbol']):
        col = df_yahoo[stock] * pf['volume'].iloc[idx]
        col.iloc[col.index < pf['order_date'].iloc[idx]] = pf['investment'].iloc[idx]
        if stock not in df.columns:
            df[stock] = col
        else:
            df[stock] = df[stock] + col

    # Group shares of same stock which have been ordered on different days
    pf = pf.groupby(by='symbol').agg({'name': lambda val: val.iloc[0],
                                      'order_date': 'min',
                                      'volume': 'sum',
                                      'investment': 'sum'})

    pf['symbol'] = pf.index
    pf = pf.sort_values('name')

    # Complete portfolio information
    pf['order_price'] = pf['investment'].div(pf['volume'])
    pf['yesterday'] = df.values[-2] / pf['volume']  # Share price yesterday
    pf['today'] = df.values[-1] / pf['volume']  # Share price today
    pf['return_yesterday'] = pf['today'] / pf['yesterday']  # Return since yesterday
    pf['return_overall'] = df.values[-1] / df.values[0]  # Overall return
    pf['value'] = pf['volume'] * pf['today']  # Current value of stock
    pf['profit'] = pf['value'] - pf['investment']  # Profit or loss

    # Normalize
    df = df.div(df.iloc[0])

    # Calculate total portfolio and comparison with MSCI world ETF
    df_pf = df.copy()
    df_wo = df.copy()

    for idx in range(len(pf)):
        order_date = pf['order_date'].iloc[idx]
        c = 0
        while True:
            try:
                v = df_yahoo.at[order_date + timedelta(days=c), ETF]
                break
            except KeyError:
                c += 1

        df_wo.iloc[:, idx] = df_yahoo[ETF] / v
        df_wo.loc[:pf['order_date'].iloc[idx], df.columns[idx]] = 1
        df_wo.iloc[:, idx] = df_wo.iloc[:, idx] * pf['investment'].iloc[idx]
        df_pf.iloc[:, idx] = df_pf.iloc[:, idx] * pf['investment'].iloc[idx]

    df_pf['My Portfolio'] = df_pf.sum(axis=1) / pf['investment'].sum()
    df_wo['MSCI World ETF'] = df_wo.sum(axis=1) / pf['investment'].sum()

    df2 = pd.concat([df_pf['My Portfolio'], df_wo['MSCI World ETF']], axis=1)
    return pf, df, df2


def get_populated_watchlist(user, df_yahoo):
    pf = load_user_portfolio(user, in_portfolio=False)

    if len(pf) == 0:
        return pf, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    pf.set_index('symbol', inplace=True)
    pf['symbol'] = pf.index

    # Populate dataframe of stocks with Yahoo data
    df = pd.DataFrame()
    for stock in pf['symbol']:
        df[stock] = df_yahoo[stock]

    # Complete portfolio information
    pf['ytd'] = df.values[max(-250, -len(df))].tolist()[:len(pf)]  # Share price 1 year ago
    pf['3ytd'] = df.values[0].tolist()[:len(pf)]  # Share price 3 years ago
    pf['yesterday'] = df.values[-2].tolist()[:len(pf)]  # Share price yesterday
    pf['today'] = df.values[-1].tolist()[:len(pf)]  # Share price today
    pf['return_yesterday'] = pf['today'] / pf['yesterday']  # Return since yesterday
    pf['return_ytd'] = pf['today'] / pf['ytd']  # Return in last year
    pf['return_3ytd'] = pf['today'] / pf['3ytd']  # Return in last 3 years

    # Normalize and set stock to 1
    for stock in pf.index:
        df.loc[:, stock] = df.loc[:, stock] / df[stock].iloc[0]

    # Calculate 90 days rolling average
    df_90 = df.copy()
    df_90 = df_90.rolling(window=90).mean()

    def analyze(st):
        if df_90[st].iloc[-1] / df[st].iloc[-1] > 1.05:
            return 'Buy'
        return 'Wait'

    pf['action'] = [analyze(stock) for stock in pf.index]

    # Analyze volatility
    df_vo = df.copy()
    df_vo = df_vo.pct_change().mul(100)
    df_vo.dropna(axis=0, inplace=True)  # First line is NaN

    # Calculate volatility
    pf['volatility'] = [(df_vo[s][df_vo[s] != 0].rolling(7).std() * np.sqrt(7)).mean() for s in df_vo.columns]

    return pf, df, df_90, df_vo


def no_stocks_response(request, message, alert, url):
    if request.POST.get('stock_to_add') or request.POST.get('stock_to_remove'):
        return JsonResponse({'message': message, 'alert': alert})
    return render(request, url, {'avatar': get_avatar(request), 'table': []})


def remove_shares(user, symbol, number):
    stocks = [(s, s.order_date) for s in user.stocks.filter(symbol=symbol, in_portfolio=True)]
    stocks.sort(key=lambda v: v[1])  # Sort by date
    for (s, _) in stocks:
        if number < s.volume:
            s.volume = s.volume - number  # reduce shares by number starting with oldest
            s.save()
            break
        number = number - s.volume  # all shares get deleted
        s.delete()


def check_stocks(user):
    # Watchlist
    stocks = user.stocks.filter(in_portfolio=False)
    df_yahoo = get_stock_data([s.symbol for s in stocks])

    pf, _, _, _ = get_populated_watchlist(user, df_yahoo)

    for s in stocks:
        if pf.loc[s.symbol]['action'] == 'Buy':
            if not user.stocks.get(symbol=s.symbol).buy_recommendation:
                content = '<p style = "color:#363457"><big>Time to buy ' + pf.loc[s.symbol]['name'] + '!</big><p>'
                send_email(user.email, 'Time to buy!', content)
                s.buy_recommendation = True
                s.save()
        else:
            s.buy_recommendation = False
            s.save()

    # Portfolio
    stocks = user.stocks.filter(in_portfolio=True)

    if len(stocks) > 0:
        first_order = min([s.order_date for s in stocks])
        df_yahoo = get_stock_data([s.symbol for s in stocks] + [ETF], min_date=first_order)

        pf, _, _ = get_populated_portfolio(user, df_yahoo)

        for s in stocks:
            change = round((pf.loc[s.symbol]['return_yesterday'] - 1) * 100, 1)
            if MIN + 1 < change < MAX - 1:
                s.today = 0  # necessary for reset
            elif change > max(MAX, s.today + 1):
                send_email(user.email, 'Yay! One of your stocks is up big time!',
                           '<p style = "color:#008000"><big>"' + pf.loc[s.symbol]['name'] + ' is up by ' +
                           str(change) + '%!"</big><p>')
                s.today = change
            elif change < min(MIN, s.today - 1):
                send_email(user.email, 'Damn! One of your stocks is down!',
                           '<p style = "color:#ff0000"><big>"' + pf.loc[s.symbol]['name'] + ' is down by ' +
                           str(change) + '%!"</big><p>')
                s.today = change
            s.save()

    update_notification(user, 'stocks', weekends=False)
