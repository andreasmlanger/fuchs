from django.http import JsonResponse
from django.shortcuts import render
import random
from main.maps import *
from main.airtable_data import fetch_json_data_from_media_folder, format_content
from main.utils import get_avatar
from .models import Data
from .utils import *


def index(request, keyword=None):
    if request.method == 'POST' and request.POST.get('task') == 'fetch':
        df = pd.read_csv(request.POST.get('map_url'))  # map data is stored as csv!
        b = create_bokeh_html(df, request.POST.get('map'))  # elevation profile, filename contains metadata on route
        icon = 'bicycle' if b else 'car'  # car routes get empty string bokeh html
        m = create_map_html(df, icon=icon, width=300, height=200)
        return JsonResponse({'map': m, 'bokeh': b})
    data = fetch_json_data_from_media_folder(request, app='travel', model=Data)
    if not request.user.is_superuser:
        data = [d for d in data if d['Date'] > '2018']  # filter for non-superusers!
    data = add_next_page(data)
    years = get_years(data)
    wordcloud = sorted(get_wordcloud(data).items())
    if keyword:
        data = filter_data(data, keyword)
    else:
        data = [random.choice(data)]
    data = add_continents(data)
    data = format_content(data)
    return render(request, 'travel/index.html', {'data': data, 'wordcloud': wordcloud, 'years': years,
                                                 'avatar': get_avatar(request)})
