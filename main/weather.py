import requests
from mysite.settings import config


WEATHER_API_KEY = config.get(f'WEATHER_API_KEY')
WEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'


def get_weather(city):
    url = f'{WEATHER_BASE_URL}?APPID={WEATHER_API_KEY}&q={city}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        description = data['weather'][0]['main']
        icon = data['weather'][0]['icon']
        icon_url = f'http://openweathermap.org/img/wn/{icon}.png'
        temperature = f"{int(data['main']['temp'] - 273.15)}°C"
    else:
        description = 'Error'
        icon_url = ''
        temperature = 'N.A.'

    return {'temperature': temperature, 'description': description, 'icon_url': icon_url}
