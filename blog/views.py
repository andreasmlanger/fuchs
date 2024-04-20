from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from main.airtable_data import fetch_json_data_from_media_folder, format_content
from main.utils import get_avatar
from .models import Data


@login_required()
def index(request):
    data = load_data(request)
    return render(request, 'blog/index.html', {'data': data, 'avatar': get_avatar(request)})


# no login required, so that it can be shared
def open_single_post(request, blog_id):
    data = load_data(request, blog_id=blog_id)
    return render(request, 'blog/index.html', {'data': data, 'avatar': get_avatar(request)})


def load_data(request, blog_id=None):
    data = fetch_json_data_from_media_folder(request, app='blog', model=Data, blog_id=blog_id)
    data = format_content(data)
    return data
