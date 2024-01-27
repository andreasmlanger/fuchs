from bs4 import BeautifulSoup
import requests


def scrape_trailers_from_apple():
    apple_website = 'https://tv.apple.com/us/room/movie--tv-trailers/edt.item.64248313-7414-4d63-a6fc-7c29f9916c79'
    site = requests.get(apple_website)
    soup = BeautifulSoup(site.content, 'lxml')
    divs_with_trailer = soup.select('.infinite-grid__body div[aria-label]')

    trailers = []
    for div in divs_with_trailer:
        # Scrape
        title = div['aria-label']
        button = div.find('button', class_='lockup-button--context-menu')
        url = button['data-metrics-click'].split('"actionUrl":"')[1].split('"')[0]
        img_url = div.find('source', {'type': 'image/webp'})['srcset'].split(',')[-1].strip().split(' ')[0].strip()

        # Extract information
        trailer = {'title': title,
                   'url': url,
                   'img_url': img_url}

        trailers.append(trailer)

    return trailers
