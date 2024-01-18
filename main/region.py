SPAIN = ['Barcelona', 'Madrid', 'Palma']
FRANCE = ['Bordeaux', 'Lyon', 'Marseille', 'Paris']


def get_region(city):
    if city in SPAIN:
        return {'country': 'Spain', 'language': 'es'}
    elif city in FRANCE:
        return {'country': 'France', 'language': 'fr'}
    return {'country': 'Germany', 'language': 'de'}  # default
