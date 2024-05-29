from django.shortcuts import render
from main.utils import get_avatar


def index(request):
    return render(request, 'tiles/index.html', {'avatar': get_avatar(request)})
