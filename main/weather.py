"""
Weather API: https://open-meteo.com/en/docs/
Icons: https://icons8.com/icon/set/weather/color-glass--static
"""

from bokeh.palettes import Plasma256, Viridis256
import pandas as pd
import requests
from datetime import datetime

WEATHER_BASE_URL = 'https://api.open-meteo.com/v1/forecast?'
CURRENT = 'temperature_2m,weather_code'
DAILY = 'weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,uv_index_max'
COLORS = (Viridis256 + Plasma256[::-1])[:420]

# WMO Codes with description and icon number
WMO_CODES = {
    0: ('clear sky', 0),
    1: ('mainly clear', 1),
    2: ('partly cloudy', 1),
    3: ('overcast', 3),
    45: ('fog', 45),
    48: ('fog', 45),
    51: ('light drizzle', 61),
    53: ('moderate drizzle', 61),
    55: ('dense drizzle', 61),
    56: ('light freezing drizzle', 61),
    57: ('dense freezing drizzle', 61),
    61: ('slight rain', 61),
    63: ('moderate rain', 63),
    65: ('heavy rain', 65),
    66: ('light freezing rain', 61),
    67: ('heavy freezing rain', 65),
    71: ('slight snow fall', 71),
    73: ('moderate snow fall', 73),
    75: ('heavy snow fall', 73),
    77: ('snow grains', 73),
    80: ('slight rain showers', 61),
    81: ('moderate rain showers', 63),
    82: ('violent rain showers', 65),
    85: ('slight snow showers', 71),
    86: ('heavy snow showers', 73),
    95: ('thunderstorm', 95),
    96: ('thunderstorm with slight hail', 95),
    99: ('thunderstorm with heavy hail', 95),
}


def get_color(x):
    return COLORS[int(max(0, min(1, (x + 20) / 50)) * len(COLORS))]


def get_weather_description(wmo_code):
    return WMO_CODES[wmo_code][0]


def get_weather_icon_url(wmo_code):
    return f'main/weather_icons/{WMO_CODES[wmo_code][1]}.png'


def get_weather_forecast(lat, lon, period='daily'):
    url = f'{WEATHER_BASE_URL}latitude={lat}&longitude={lon}&timezone=auto&current={CURRENT}&daily={DAILY}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if period == 'current':
            forecast = {
                'temperature': int(data['current']['temperature_2m']),
                'description': get_weather_description(data['current']['weather_code']),
                'icon_static_url': get_weather_icon_url(data['current']['weather_code'])
            }
            return {'weather_forecast': forecast}

        elif period == 'daily':
            df = pd.DataFrame(data['daily'])
            df.rename(columns={'temperature_2m_max': 'max', 'temperature_2m_min': 'min'}, inplace=True)
            df['weekday'] = df['time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%a'))
            df['sunrise'] = df['sunrise'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M').strftime('%H:%M'))
            df['sunset'] = df['sunset'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M').strftime('%H:%M'))
            df['bar_height'] = (df['max'] - df['min']) * 9
            df['description'] = df['weather_code'].apply(get_weather_description)
            df['icon_static_url'] = df['weather_code'].apply(get_weather_icon_url)

            temp_hi = df['max'].max()
            temp_lo = df['min'].min()

            df['bar_offset_t'] = (temp_hi - df['max']) * 9
            df['bar_offset_b'] = (df['min'] - temp_lo) * 9
            df['color'] = ((df['max'] + df['min']) / 2).apply(get_color)

            return {'weather_forecast': df.to_records()}

    return {'weather_forecast': 0}
