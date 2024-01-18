from datetime import timedelta
from main.region import get_region

WAITING_TIME = {
    0: timedelta(hours=0),
    1: timedelta(hours=6),
    2: timedelta(days=1),
    3: timedelta(days=2),
    4: timedelta(days=4),
    5: timedelta(days=8),
    6: timedelta(days=16),
    7: timedelta(days=32),
    8: timedelta(days=64),
    9: timedelta(days=128),
    10: timedelta(days=256),
}

# https://www.flaticon.com/packs/countrys-flags
LANGUAGES = ['en', 'fr', 'es', 'pt', 'jp', 'de']

BATCH_SIZE = 20  # batch size for study session
BATCH_SIZE_VERBS = 10  # batch size for study session


def get_languages(request):
    city = request.user.profile.city
    languages = LANGUAGES.copy()
    languages.remove(get_region(city)['language'])
    return languages
