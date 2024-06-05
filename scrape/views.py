from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from main.utils import get_avatar, is_due
from .models import Keyword, Kleinanzeigen, Urlaubspiraten
from .scrape import *


@login_required
def index(request):
    if request.POST:
        if request.POST.get('task') == 'delete':
            Keyword.objects.get(id=request.POST.get('id')).delete()
        elif request.POST.get('task') == 'scrape' and is_due(request.user, 'scrape'):
            scrape(request.user, 'kleinanzeigen', 'urlaubspiraten')
        return HttpResponse()
    return render(request, 'scrape/index.html', {'keywords': get_keywords(request.user),
                                                 'avatar': get_avatar(request)})


def get_keywords(user):
    values = ['id', 'keyword', 'price', 'distance']
    keywords_kleinanzeigen = user.kleinanzeigen.all().values(*values).order_by('keyword')
    for k in keywords_kleinanzeigen:
        k['website'] = 'kleinanzeigen'
        k['url'] = get_url(k['website'], keyword=k['keyword'], price=k['price'], distance=k['distance'])
        del k['price']  # not needed in frontend!
        del k['distance']  # not needed in frontend!
    values = ['id', 'keyword']
    keywords_urlaubspiraten = user.urlaubspiraten.all().values(*values).order_by('keyword')
    for k in keywords_urlaubspiraten:
        k['website'] = 'urlaubspiraten'
        if k['keyword'].startswith('~'):
            k['blacklist'] = 1  # blacklist
            k['keyword'] = k['keyword'][1:]  # strip ~
        else:
            k['blacklist'] = 0  # whitelist
    return list(keywords_kleinanzeigen) + list(keywords_urlaubspiraten)


def add_keyword(request):
    website = request.POST.get('website')
    params = {'user': request.user, 'keyword': request.POST.get('keyword')}
    if website == 'kleinanzeigen':
        params['price'] = None if request.POST.get('price') == 'Unlimited' else request.POST.get('price').split()[0]
        params['distance'] = request.POST.get('distance').split()[0]
        Kleinanzeigen(**params).save()
    elif website == 'urlaubspiraten':
        Urlaubspiraten(**params).save()
    return render(request, 'scrape/main.html', {'keywords': get_keywords(request.user), 'website': website})
