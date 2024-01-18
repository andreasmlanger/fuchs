from datetime import datetime


CONTINENTS = {'europe': ['Deutschland', 'Frankreich', 'Island', 'Österreich', 'Schweiz', 'Spanien'],
              'asia': ['China', 'Indonesien', 'Japan', 'Kambodscha', 'Laos', 'Myanmar', 'Oman', 'Philippinen',
                       'Qatar', 'Sri Lanka', 'Thailand', 'VAE', 'Vietnam'],
              'americas': ['Argentinien', 'Bolivien', 'Brasilien', 'Chile', 'Costa Rica', 'Ecuador', 'Kanada',
                           'Kolumbien', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'USA'],
              'oceania': ['Australien', 'Fiji', 'Hawaii', 'Neuseeland']}

# JS to format y-axis labels of bokeh profile plot as meters
FORMAT_METERS = """
    if (tick.toString().length > 14) {
        tick = parseFloat(tick.toString().slice(0, tick.toString().length - 2))
    }
    return tick + 'm'
    """


def add_continents(data):
    for article in data:
        article['Continent'] = get_continent(article['Tags'][0])
    return data


def add_next_page(data):
    for i in range(len(data) - 1):
        data[i]['NextDate'] = data[i + 1]['Date']
    return data


def filter_data(data, kw):
    if kw[0].isdigit():  # year or date
        if len(kw) == 4:  # year
            data = filter(lambda x: x['Date'].split('-')[0] == kw, data)
        else:  # date in format YYYY-MM-DD
            data = filter(lambda x: x['Date'] == kw, data)
    else:  # country
        data = filter(lambda x: kw.replace('-', ' ') in [t.lower() for t in x['Tags']], data)
    return list(data)


def get_continent(country):
    for continent, countries in CONTINENTS.items():
        if country in countries:
            return continent


def get_wordcloud(data, min_pt=10, max_pt=20):
    cloud = {}
    for article in data:
        for tag in article['Tags']:
            if tag not in cloud:
                cloud[tag] = 1
            else:
                cloud[tag] += 1
    for tag in cloud.keys():
        cloud[tag] = min(cloud[tag], 28)  # cutoff max
    counts = cloud.values()
    min_count, max_count = min(counts), max(counts)
    for tag in cloud.keys():
        if min_count < max_count:
            cloud[tag] = int((cloud[tag] - min_count) / (max_count - min_count) * (max_pt - min_pt) + min_pt)
        else:
            cloud[tag] = 14  # only one
    return cloud


def get_years(data):
    return sorted(set(datetime.strptime(d['Date'], '%Y-%m-%d').strftime("%y") for d in data))
