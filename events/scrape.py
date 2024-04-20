from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import json
import random
import requests
import threading
import urllib.parse
from main.emails import send_email, send_error_email
from main.utils import update_notification
from .utils import check_city


PARALLEL = 10


def scrape_events(city, page, in_parallel=False):
    results = {}  # dictionary to store scraped data from threads
    scrape_meetup(city, results)
    if in_parallel:
        # return scrape_eventbrite_in_multithread(results, city)
        pass
    return scrape_eventbrite_page_by_page(results, city, page)


def scrape_eventbrite_page_by_page(results, city, page):
    scrape_eventbrite(results, city, page)
    return results


def scrape_eventbrite_in_multithread(results, city, start=0, stop=100):
    threading.excepthook = lambda args: send_error_email(args.exc_value)  # catch exceptions in threads
    i = start
    while i < stop:  # break condition to avoid infinite increment
        threads = []
        for i in range(i + 1, i + 1 + PARALLEL):
            t = threading.Thread(target=scrape_eventbrite, args=(results, city, i))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()  # wait for all threads to end
        if 'STOP' in results.keys():
            print('OK')
            break
    return results


def scrape_eventbrite(results, city, page):
    url = f'https://www.eventbrite.de/d/de--{city}/free--events/?page={page}'
    print(url)
    site = requests.get(url)
    soup = BeautifulSoup(site.content, 'lxml')
    script = soup.find_all('script', attrs={'type': 'application/ld+json'})[:]  # convert to list
    if script:
        data = [json.loads(s.text) for s in script]
        data = extract_relevant_information(data, website='eventbrite', city=city)
        results[page] = data
    else:  # empty list evaluates as false
        results['STOP'] = []  # stop condition


def scrape_meetup(city, results):
    t1, t2 = random.choice([(0, 7), (7, 14), (14, 28), (28, 56)])

    today = datetime.now().date()
    start_date = today + timedelta(days=t1)
    end_date = today + timedelta(days=t2)

    def format_date(d):
        return f'{d.strftime("%Y-%m-%d")}T17%3A59%3A00-04%3A00'

    query = [f'source=EVENTS',
             f'location=de--{urllib.parse.quote(city)}',
             f'keywords={random.choice(["Product", "Programming", "Science", "Technology"])}',
             f'distance=tenMiles',
             f'eventType=inPerson',
             f'customStartDate={format_date(start_date)}',
             f'customEndDate={format_date(end_date)}',
             ]

    url = f'https://www.meetup.com/find/?{"&".join(query)}'
    print(url)
    site = requests.get(url)
    soup = BeautifulSoup(site.content, 'lxml')
    script = soup.find_all('script', attrs={'type': 'application/ld+json'})[1:]
    if script:
        data = [json.loads(s.text) for s in script][0]
        data = extract_relevant_information(data, website='meetup')
        results[0] = data  # meetup is saved as key '0' in results dictionary
        print(f'Meetup')


def extract_relevant_information(data, website, city=None):
    if website == 'eventbrite':
        data = data[0]['itemListElement']
        data = [d['item'] for d in data]
    data = filter_only_valid_locations(data, city)
    for i in range(len(data)):
        data[i] = {'website': website,
                   'date': data[i]['startDate'][:10],  # crop to YYYY-MM-DD
                   'event': data[i]['name'],
                   'location': data[i]['location']['name'],
                   'url': data[i]['url'],
                   'latitude': data[i]['location']['geo']['latitude'],
                   'longitude': data[i]['location']['geo']['longitude'],
                   'group': data[i]['performer'] if 'performer' in data[i] else ''}
    return data


def filter_only_valid_locations(data, city):
    filtered_data = []
    for i in range(len(data)):
        if 'location' not in data[i]:
            continue
        elif isinstance(data[i]['location'], list):
            for location in data[i]['location']:
                if 'name' in location:
                    data[i]['location'] = location  # remove virtual locations
                    break
            else:
                continue
        elif 'name' not in data[i]['location'] or 'geo' not in data[i]['location']:
            continue
        if check_city(data[i]['location']['address']['addressLocality'], city):
            filtered_data.append(data[i])
    return filtered_data


def filter_new_events(user, events):
    new_events = []
    user_events = set([(str(b.date), b.event, b.location) for b in user.events.all()])
    blacklist_0 = [b.name for b in user.blacklist.filter(type=0)]  # events
    blacklist_1 = [b.name for b in user.blacklist.filter(type=1)]  # locations
    blacklist_2 = [b.name for b in user.blacklist.filter(type=2)]  # groups
    for batch in events.values():
        for e in batch:
            try:
                if e['date'] < str(date.today()):  # past events
                    continue
                if (e['date'], e['event'], e['location']) in user_events:  # event already exists
                    continue
                if any(b in e['event'] for b in blacklist_0):
                    continue
                if any(b in e['location'] for b in blacklist_1):
                    continue
                if any(b in e['group'] for b in blacklist_2):
                    continue
                new_events.append(e)
            except (AttributeError, UnicodeDecodeError):
                pass

    return new_events


def send_events_email(user, events):
    html = '<html><body>'
    items = sorted(events, key=lambda e: e['date'])
    for i in items:
        html += f'<p>{i["date"]}<br>{i["location"]}<br><a href="{i["url"]}">{i["event"]}</a><br></p>'
    html += '</body></html>'
    send_email(user.email, 'New events found!', html)
    update_notification(user, app='events')
