import requests
from datetime import datetime
from mysite.settings import config


WEATHER_API_KEY = config.get(f'WEATHER_API_KEY')
WEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5/'


def get_weather_now(city):
    url = f'{WEATHER_BASE_URL}weather?APPID={WEATHER_API_KEY}&q={city}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        description = data['weather'][0]['main']
        icon_static_url = get_static_weather_icon_url(data['weather'][0]['icon']).replace('n.png', 'd.png')
        temperature = format_temperature_in_celsius(data['main']['temp'])
    else:
        description = 'Error'
        icon_static_url = ''
        temperature = 'N.A.'

    return {'temperature': temperature, 'description': description, 'icon_static_url': icon_static_url}


def get_static_weather_icon_url(icon_code):
    return f'main/weather_icons/{icon_code}.png'


def format_temperature_in_celsius(t):
    return int(round(t - 273.15, 0))


def get_coordinates(city):
    base_url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': city,
        'format': 'json',
        'limit': 1
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data:
        return {'Latitude': float(data[0]['lat']), 'Longitude': float(data[0]['lon'])}


def get_weather_forecast(city):
    coords = get_coordinates(city)
    lat, lon = coords['Latitude'], coords['Longitude']
    url = f'{WEATHER_BASE_URL}onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={WEATHER_API_KEY}'
    response = requests.get(url)

    def timestamp_to_date(timestamp, style):
        return datetime.fromtimestamp(timestamp).strftime(style)

    if response.status_code == 200:
        data = response.json()
        forecast = []
        for d in data['daily']:
            w = {
                'weekday': timestamp_to_date(d['dt'], style='%a %d'),
                'sunrise': timestamp_to_date(d['sunrise'], style='%H:%M'),
                'sunset': timestamp_to_date(d['sunset'], style='%H:%M'),
                'min': format_temperature_in_celsius(d['temp']['min']),
                'max': format_temperature_in_celsius(d['temp']['max']),
                'bar_height': (d['temp']['max'] - d['temp']['min']) * 10,
                'weather': d['weather'][0]['main'],
                'description': d['weather'][0]['description'],
                'icon_static_url': get_static_weather_icon_url(d['weather'][0]['icon']),
                'clouds': d['clouds'],
                'rain': d['rain'] if 'rain' in d else 0,
                'uvi': d['uvi'],
            }
            forecast.append(w)
        temp_hi = max([w['max'] for w in forecast])
        temp_lo = min([w['min'] for w in forecast])
        for w in forecast:
            w['bar_offset_t'] = (temp_hi - w['max']) * 10
            w['bar_offset_b'] = (w['min'] - temp_lo) * 10
    else:
        forecast = 'Error'

    return {'weather_forecast': forecast}
