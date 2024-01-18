from django.shortcuts import render
from main.utils import get_avatar


def index(request):
    return render(request, 'frog/index.html', {'avatar': get_avatar(request)})
