from PIL import Image
import requests
import base64
from datetime import date, datetime, timedelta
from io import BytesIO
import math


APPS = {'events': {'description': 'Eventbrite & Meetup events', 'time_delta': timedelta(minutes=10)},
        'quotes': {'description': 'Quote of the day', 'time_delta': timedelta(hours=24)},
        'scrape': {'description': 'Kleinanzeigen & Urlaubspiraten', 'time_delta': timedelta(minutes=10)},
        'stocks': {'description': 'Portfolio & Watchlist', 'time_delta': timedelta(hours=1)},
        'vocabulary': {'description': 'Vocabulary to study', 'time_delta': timedelta(minutes=10)}}

ONLINE = 5  # hour of day when notifications start
OFFLINE = 23  # hour of day when notifications end


def get_avatar(request):
    try:
        return decode_bytes(request.user.profile.avatar)
    except AttributeError:
        return None


def get_lat_and_lon(city):
    base_url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': city,
        'format': 'json',
        'limit': 1
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None


def decode_bytes(b):
    if isinstance(b, bytes):
        return b.decode('utf-8')
    return b.tobytes().decode('utf-8')


def uploaded_image_to_base64(upload, w=192, h=192):
    im = Image.open(BytesIO(upload.file.getvalue()))
    im = crop_and_resize_image(im, w, h)
    return base64.b64encode(im)


def crop_and_resize_image(im, w, h):
    orig_w, orig_h = im.size  # original width and height
    aspect_ratio_orig = orig_w / float(orig_h)
    aspect_ratio_desired = w / float(h)

    if aspect_ratio_orig > aspect_ratio_desired:
        # Image is wider than desired aspect ratio, crop sides
        new_w = int(orig_h * aspect_ratio_desired)
        crop_w = orig_w - new_w
        left = crop_w
        top = 0
        right = orig_w - crop_w
        bottom = orig_h
    else:
        # Image is taller than desired aspect ratio, crop top and bottom
        new_h = int(orig_w / aspect_ratio_desired)
        crop_h = orig_h - new_h
        left = 0
        top = crop_h
        right = orig_w
        bottom = orig_h - crop_h

    im = im.crop((left, top, right, bottom))
    im = im.resize((w, h), Image.LANCZOS)
    buffered = BytesIO()
    im.save(buffered, format='PNG', optimize=True)  # PNG has larger file size but better quality
    return buffered.getvalue()


def is_due(user, app):
    return int(datetime.now() > user.notifications.get(app=app).due)


def update_notification(user, app, weekends=True, time_delta=None, hour=None):
    midnight = datetime.combine(date.today(), datetime.min.time())
    now = datetime.now()
    if hour:
        next_time = midnight + timedelta(hours=hour)
    else:
        time_delta = time_delta if time_delta else APPS[app]['time_delta']  # get default for app
        next_time = now + time_delta
    if next_time.hour < ONLINE or next_time.hour > OFFLINE or (not weekends and next_time.weekday() in (5, 6)):
        next_time = midnight + timedelta(hours=ONLINE)  # next notification at ONLINE hour
    while next_time < now:
        next_time = next_time + timedelta(days=1)  # increment days until valid day in the future
    user.notifications.filter(app=app).update(due=next_time)


def date_to_string(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")


def round_down_to_next_100(x):
    return math.floor(x / 100) * 100


def round_up_to_next_100(x):
    return math.ceil(x / 100) * 100
