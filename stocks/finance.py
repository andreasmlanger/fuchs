"""
Use Yahoo Finance to obtain stock information
"""


import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time


def get_stock_data(tickers, new_stock=None, min_date=None, new_date=None):
    if new_date:  # new stock added to portfolio
        date_to_fetch = min(min_date, datetime.strptime(new_date, '%b %d, %Y'))
    elif min_date:  # portfolio with no stock added
        date_to_fetch = min_date
    else:  # watchlist
        date_to_fetch = datetime.now() - timedelta(days=3 * 365)

    if new_stock:
        try:
            return load_from_yahoo([new_stock] + tickers, date_to_fetch)
        except Exception as ex:
            print('New stock has crashed Yahoo!', ex)

    if len(tickers) > 0:
        return load_from_yahoo(tickers, date_to_fetch)


def load_from_yahoo(stocks, date):
    start = date - timedelta(days=7)  # always start 1 week earlier to catch holidays
    end = datetime.today()

    print('Fetching stocks from Yahoo finance')
    attempt, max_attempts = 0, 10
    while True:
        try:
            df = yf.download(stocks, start, end, threads=False)  # threads=True sometimes leads to errors
            break
        except Exception as ex:
            print(ex)
            attempt += 1
            if attempt < 10:
                print(f"Error fetching today's stocks, trying again ({attempt}/{max_attempts})")
                time.sleep(0.5)
            else:
                print("Error fetching today's stocks, getting data from yesterday instead")
                try:  # try to use yesterday if today gives an error
                    df = yf.download(stocks, start, end - timedelta(days=1))
                    today = yf.download(stocks, end - timedelta(days=1), end).fillna(method='ffill')
                    today = today.drop(today.index[0])
                    df = pd.concat([df, today], ignore_index=True)
                    break
                except Exception as ex:
                    print(ex)
                    return

    df = df['Close']  # only get 'Close'
    df = df.reindex().fillna(method='ffill').fillna(method='bfill')  # fill NaN values

    if isinstance(df, pd.Series):  # no ticker header if only one
        df = df.to_frame()
        df.columns = stocks

    df = df.dropna(axis=1)

    for idx, t in enumerate(df.index.tolist()):
        if t >= date:
            return df.iloc[max(0, idx - 1):]  # return df with one day before start date
