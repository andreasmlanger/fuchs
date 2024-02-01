from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UpdateProfile
from .scheduler import run_scheduling
from .utils import *
from .weather import get_weather_forecast, get_weather_now


@login_required
def home(request):
    return render(request, 'main/home.html', {'avatar': get_avatar(request)})


def scheduler(request, job):
    return render(request, 'main/scheduler.html', {'status': run_scheduling(job)})


@login_required
def account(request):
    user = request.user
    if request.method == 'POST':
        if request.POST.get('delete_account'):
            if user.is_superuser:
                messages.add_message(request, messages.WARNING, 'Superusers cannot delete their account!')
                return HttpResponseRedirect('/account')
            user.delete()
            return HttpResponseRedirect('/login')
        form = UpdateProfile(request.POST, request.FILES)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.profile.city = form.cleaned_data['city']
            user.email = form.cleaned_data['email']
            if request.FILES.get('avatar'):
                user.profile.avatar = get_avatar_image(form.cleaned_data['avatar'])
            user.save()

            for app in APPS.keys():
                notification = user.notifications.get(app=app)
                if notification.email != bool(request.POST.get(f'{app}_notification')):
                    notification.email = not notification.email
                    if not notification.email:
                        notification.due = datetime.now()  # reset notifications
                    notification.save()

            messages.add_message(request, messages.SUCCESS, 'Your profile was successfully updated!')
        else:
            if 'image' in str(form.errors):
                message = 'No valid profile picture!'
            elif 'email' in form.errors:
                message = 'Please enter a valid email address!'
            else:
                message = 'Invalid input!'
            messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect('/account')

    profile = {'user_name': user,
               'first_name': user.first_name,
               'last_name': user.last_name,
               'city': user.profile.city,
               'email': user.email,
               'avatar': get_avatar(request)}

    apps = APPS.copy()
    if user.profile.city != 'München':
        del apps['events']
    for app in apps.keys():
        apps[app]['notification'] = user.notifications.get(app=app).email

    # Weather API
    weather_now = get_weather_now(user.profile.city)

    return render(request, 'main/account.html', profile | weather_now | {'apps': apps})


@login_required
def weather(request):
    # Weather API
    weather_forecast = get_weather_forecast(request.user.profile.city)

    return render(request, 'main/weather.html', weather_forecast | {'avatar': get_avatar(request)})
