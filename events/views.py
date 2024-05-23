from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from main.utils import get_avatar, is_due
from mysite.settings import config
from .models import BlackList, Event
from .scrape import *
from .utils import *


@login_required
def index(request):
    if request.method == 'POST':
        if request.POST.get('task') == 'blacklist':
            add_item_to_blacklist(request.user, request.POST.get('name'), int(request.POST.get('type')))
        elif request.POST.get('task') == 'attend':
            request.user.events.filter(id=request.POST.get('id')).update(**{'attending': request.POST.get('attending')})
        elif request.POST.get('task') == 'remove':
            request.user.events.filter(id=request.POST.get('id')).update(**{'hidden': True})
        elif request.POST.get('task') == 'scrape':
            page = random.randint(1, 10)  # random Eventbrite page to scrape
            events = json.loads(request.POST.get('events'))  # obtain events dictionary from frontend
            new_events = scrape_events(request.user.profile.city, page, in_parallel='RENDER' not in config)
            update_notification(request.user, app='events')
            events = events | new_events
            new_events = filter_and_save_new_events(request.user, events)
            return JsonResponse({'number': len(new_events)})
        return HttpResponse()

    delete_past_events()  # for all users, also inactive ones

    return render(request, 'events/index.html', {'avatar': get_avatar(request), 'color': COLOR,
                                                 'events': load_events(request.user),
                                                 'is_due': is_due(request.user, 'events')})


def load_events(user):
    values = ['id', 'website', 'date', 'event', 'location', 'url', 'attending', 'latitude', 'longitude', 'group',
              'created_at']
    events = list(user.events.filter(hidden=False).values(*values).order_by('date', 'event'))
    for e in events:
        e['attending'] = int(e['attending'])
        e['weekday'] = WEEKDAYS[e['date'].weekday()]
        e['date_string'] = e['date'].strftime('%m/%d/%Y')
        e['new'] = int((date.today() - e['created_at']).days < 2)  # new if less than 2 days old
    return events


def add_item_to_blacklist(user, name, blacklist_type):
    if not user.blacklist.filter(name=name, type=blacklist_type).exists():
        b = BlackList(user=user, name=name, type=blacklist_type)
        b.save()
        remove_events_based_on_blacklist_item(user, b)


def remove_events_based_on_blacklist_item(user, b):
    for e in user.events.all():
        if b.type == 0 and b.name in e.event:
            e.delete()
        elif b.type == 1 and b.name in e.location:
            e.delete()
        elif b.type == 2 and b.name in e.group:
            e.delete()


def delete_past_events():
    for e in Event.objects.all():
        if e.date < date.today():
            e.delete()


def filter_and_save_new_events(user, events):
    new_events = filter_new_events(user, events)
    Event.objects.bulk_create([Event(**e, user=user) for e in new_events])
    return new_events


def refresh_events_grid(request):
    return render(request, 'events/main.html', {'events': load_events(request.user), 'color': COLOR})


def check_for_new_events(city):
    print(f'Searching for free events in {city} on Eventbrite.com')
    events = {}
    for page in random.sample(range(20), 5):
        events = events | scrape_events(city, page + 1)
    return events


def events_muc(_):
    user = User.objects.filter(is_superuser=True).first()
    events = load_events(user)
    events = [e for e in events if e['attending']]
    return JsonResponse(events, safe=False)
