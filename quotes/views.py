from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
import random
from main.emails import send_email
from main.utils import get_avatar, update_notification
from .models import Quote


@login_required
def index(request):
    if request.POST.get('task') == 'delete':
        request.user.quotes.get(id=request.POST.get('id')).delete()
        return HttpResponse()
    return render(request, 'quotes/index.html', {'quotes': load_quotes(request.user), 'avatar': get_avatar(request)})


def load_quotes(user):
    values = ['id', 'quote', 'created_at']
    quotes = user.quotes.all().values(*values).order_by('-created_at')
    return quotes


def add_quote(request):
    Quote(user=request.user, quote=request.POST.get('quote')).save()
    return render(request, 'quotes/main.html', {'quotes': load_quotes(request.user)})


def send_daily_quotes_email(user):
    user_quotes = [q.quote for q in user.quotes.all()]
    if len(user_quotes) > 0:
        html = '<p style = "color:#363457"><big>"' + random.choice(user_quotes) + '"</big><p>'
        send_email(user.email, 'Quote of the Day', html)
    update_notification(user, 'quotes', hour=11)  # always at 11am
