from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from main.utils import get_avatar
from .models import Trailer
from .scrape import scrape_trailers_from_apple


@login_required
def index(request):
    if request.method == 'POST':
        t = request.user.trailer.get(id=int(request.POST.get('id')))
        t.muted = int(request.POST.get('muted'))
        t.save()
        return HttpResponse()
    trailers = load_trailers(request.user)
    return render(request, 'trailer/index.html', {'trailers': trailers, 'avatar': get_avatar(request)})


def load_trailers(user):
    # Get trailers from Apple
    apple_trailers = scrape_trailers_from_apple()

    # Get trailers stored in user database
    values = ['id', 'title', 'url', 'img_url', 'muted', 'created_at']
    user_trailers = user.trailer.all().values(*values).order_by('-created_at')

    # Create dictionary of trailers with title as key and (muted, id) as value
    user_trailer_dict = dict(zip([t['title'] for t in user_trailers], [(t['muted'], t['id']) for t in user_trailers]))

    # Add new Apple trailers to database
    for t in apple_trailers:
        if t['title'] in user_trailer_dict.keys():
            t['muted'], t['id'] = user_trailer_dict[t['title']]
        else:
            new_trailer = Trailer(user=user, title=t['title'], url=t['url'], img_url=t['img_url'])
            new_trailer.save()
            t['muted'], t['id'] = False, new_trailer.pk

    # Delete obsolete trailers if they have been muted
    apple_ids = set([t['id'] for t in apple_trailers])
    for t in user_trailers:
        if t['id'] not in apple_ids and t['muted'] and is_older_than_one_year(t['created_at']):
            user.trailer.get(id=t['id']).delete()  # clean up after one year

    return user_trailers


def is_older_than_one_year(d):
    return datetime.now() - d > timedelta(days=365)
