from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
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
    # Trailers from Apple
    apple_trailers = scrape_trailers_from_apple()

    # Trailers saved by user
    values = ['id', 'title', 'url', 'img_url', 'muted']
    user_trailers = user.trailer.all().values(*values)
    user_trailer_dict = dict(zip([t['title'] for t in user_trailers], [(t['muted'], t['id']) for t in user_trailers]))

    # Add new Apple trailers to database
    for t in apple_trailers:
        if t['title'] in user_trailer_dict.keys():
            t['muted'], t['id'] = user_trailer_dict[t['title']]
        else:
            new_trailer = Trailer(user=user, title=t['title'], url=t['url'], img_url=t['img_url'])
            new_trailer.save()
            t['muted'], t['id'] = False, new_trailer.pk

    # Delete obsolete trailers
    apple_ids = set([t['id'] for t in apple_trailers])
    for t in user_trailers:
        if t['id'] not in apple_ids:
            user.trailer.get(id=t['id']).delete()

    return apple_trailers
