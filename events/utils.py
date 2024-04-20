ALTERNATIVE_CITY_NAMES = {'München': ['München', 'Munich', 'Muenchen']}
COLOR = {'attending': '#387D7A', 'new': '#5E239D', 'else': '#6C6F7F'}
WEEKDAYS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']


def check_city(x, user_city):
    if user_city in ALTERNATIVE_CITY_NAMES:
        return x in ALTERNATIVE_CITY_NAMES[user_city]
    return True
