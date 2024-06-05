from bs4 import BeautifulSoup
import requests
from datetime import datetime
import json
import random
import re
from main.emails import send_email
from main.utils import update_notification

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.97 Safari/537.36')
HEADERS = {'User-Agent': USER_AGENT}


def get_url(website, keyword=None, price=None, distance=None):
    if website == 'kleinanzeigen':
        stem = f'https://www.kleinanzeigen.de/s-81667'
        if price:
            return f'{stem}/preis::{price}/{keyword.replace(" ", "-")}/k0l6411r{distance}'
        return f'{stem}/{keyword.replace(" ", "-")}/k0l6411r{distance}'
    return 'https://www.urlaubspiraten.de/fluege'  # Urlaubspiraten


def get_soup(url):
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


def scrape(user, *args):
    for website in args:
        keywords = user.kleinanzeigen.all() if website == 'kleinanzeigen' else user.urlaubspiraten.all()
        if website == 'kleinanzeigen':
            items = []
            # Search for a max of 3 keywords
            for k in random.sample(list(keywords), min(len(keywords), 3)):
                items.extend(scrape_kleinanzeigen(k))
        else:
            items = scrape_urlaubspiraten(keywords)
        if len(items) > 0:
            send_scraping_email(user, website, items)
        else:
            print(f'No new {website} offers found.')
    update_notification(user, 'scrape')


def scrape_kleinanzeigen(k):
    print(f'Kleinanzeigen: {k}')
    url = get_url('kleinanzeigen', k.keyword, k.price, k.distance)
    print(url)
    soup = get_soup(url)
    posts = soup.find_all('div', class_='aditem-main')  # all posts share this class name
    items = []
    for x in posts:
        d = dict()
        try:
            d['Price'] = get_kleinanzeigen_price(x)
            if k.price and d['Price'] > k.price:
                continue
            d['Location'] = get_kleinanzeigen_location(x)
            d['Distance'] = get_kleinanzeigen_distance(d['Location'])
            if k.distance and d['Distance'] > k.distance:
                continue
            d['Url'] = get_kleinanzeigen_url(x)
            d['Id'] = get_kleinanzeigen_id(d['Url'])
            if d['Id'] <= k.latest_id:
                continue
            d['Title'] = get_kleinanzeigen_title(x)
            items.append(d)
        except AttributeError:
            pass
    if len(items) > 0:
        k.latest_id = max([i['Id'] for i in items])
        k.save()
    return items


def retrieve_urlaubspiraten_json_object(js_snippet):
    json_start_index = js_snippet.find('{', js_snippet.find('__STATE__'))
    json_end_index = js_snippet.rfind('}') + 1
    json_part = js_snippet[json_start_index:json_end_index]

    # Count curly brackets and return once the first complete bracket is found
    counter = 0
    for i, char in enumerate(json_part):
        if char == '{':
            counter += 1
        elif char == '}':
            counter -= 1
        if counter == 0:  # first bracket is closed again
            return json_part[:i + 1]


def find_urlaubspiraten_posts(json_obj):
    data = json.loads(json_obj)
    return [data[key] for key in data.keys() if key.startswith('Post:')]


def scrape_urlaubspiraten(keywords):
    url = get_url('urlaubspiraten')
    soup = get_soup(url)
    js_elements = soup.find_all('script', attrs={'type': 'text/javascript'})
    if len(js_elements) == 0:
        print('Error loading JS information from Urlaubspiraten!')
        return []  # page not properly loaded, abort
    js_snippet = js_elements[0].text
    json_obj = retrieve_urlaubspiraten_json_object(js_snippet)
    posts = find_urlaubspiraten_posts(json_obj)
    items = []
    first_datetime = None  # will be set if there's a new post
    keyword_list = list(keywords)
    whitelist = [k for k in keyword_list if not k.keyword.startswith('~')]  # will shrink during loop
    blacklist = [k for k in keyword_list if k.keyword.startswith('~')]
    for x in posts:
        publication_datetime = datetime.fromisoformat(x['sys']['publishedAt'][:-1])
        whitelist = [k for k in whitelist if k.latest_datetime and k.latest_datetime < publication_datetime]
        if len(whitelist) == 0:
            break  # we're done
        if not first_datetime:
            first_datetime = publication_datetime

        # Scrape json object and store information in dictionary
        item = {'Title': x['title'],
                'Subtitle': x['subtitle'],
                'Price': x['pricing']['amount'] if x['pricing'] else None,
                'Url': f'https://www.urlaubspiraten.de/fluege/{x["slug"]}',
                }

        # Check if title contains blacklisted keyword
        if any(k.keyword in item['Title'] for k in blacklist):
            if any(k.keyword in item['Title'] + item['Subtitle'] for k in whitelist):
                pass  # whitelist can overrule blacklist
            else:
                continue
        items.append(item)
    if first_datetime:
        keywords.update(latest_datetime=first_datetime)
    return items


def send_scraping_email(user, website, items):
    html = '<html><body>'
    if website == 'kleinanzeigen':
        subject = 'Neue Kleinanzeigen!'
        for i in items:
            html += f'<a href="{i["Url"]}">{i["Title"]}</a> - {i["Price"]}€ - {i["Location"]}<br>'
    else:
        subject = 'Urlaubspiraten!'
        for i in items:
            price_info = f' - {i["Price"]}' if i['Price'] is not None else ''
            html += f'<a href="{i["Url"]}">{i["Title"]}</a>{price_info}<br>'
    html += '</body></html>'
    send_email(user.email, subject, html)


"""
Kleinanzeigen
"""


def get_number(x):
    try:
        return int(re.sub('[^0-9]', '', x))
    except ValueError:
        return 0


def get_kleinanzeigen_price(x):
    x = ' '.join(x.find('p', class_='aditem-main--middle--price-shipping--price').text.strip().split())
    if x == 'Zu verschenken':
        return 0
    return get_number(x)


def get_kleinanzeigen_location(x):
    return ' '.join(x.find('div', class_='aditem-main--top--left').text.strip().split())


def get_kleinanzeigen_distance(x):
    x = x.split('(')[-1].split(')')[0]  # get value within brackets
    return get_number(x)


def get_kleinanzeigen_url(x):
    return 'https://www.kleinanzeigen.de' + x.find('a', class_='ellipsis')['href']


def get_kleinanzeigen_id(x):
    return int(x.split('/')[-1].split('-')[0])


def get_kleinanzeigen_title(x):
    return x.find('a', class_='ellipsis').text
