from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from datetime import datetime, timedelta
from main.utils import decode_bytes, get_avatar
from .models import Message, Secret


@login_required
def index(request):
    secret = get_secret(request.user)
    if request.method == 'POST':
        secret.text = request.POST.get('text')
        secret.save()
    messages, profile_pictures = load_all_messages()
    return render(request, 'safe/index.html', {'avatar': get_avatar(request), 'text': secret.text,
                                               'messages': messages, 'profile_pictures': profile_pictures})


def get_secret(user):
    if len(user.secrets.all()) == 0:
        Secret(user=user, text='').save()  # create empty secret
    return user.secrets.all()[0]


def load_all_messages():
    profile_pictures = {}
    values = ['id', 'created_at', 'message', 'user']
    messages = Message.objects.all().values(*values).order_by('created_at')
    messages = delete_old_message(messages)
    for m in messages:
        m['message'] = m['message'].split('\n')  # array which can be rejoined by <br/> in HTML later
        user_id = m['user']
        if user_id not in profile_pictures:
            profile_pictures[user_id] = decode_bytes(User.objects.get(id=user_id).profile.avatar)
    return messages, profile_pictures


def add_message(request):
    if request.POST.get('message'):
        Message(user=request.user, message=request.POST.get('message')).save()
    messages, profile_pictures = load_all_messages()
    return render(request, 'safe/main.html', {'messages': messages[::-1], 'profile_pictures': profile_pictures})


def delete_old_message(messages, days=7):  # delete messages older than 7 days
    messages_to_keep = []
    for m in messages:
        if datetime.now() - m['created_at'] > timedelta(days=days):
            Message.objects.get(id=m['id']).delete()
        else:
            messages_to_keep.append(m)
    return messages_to_keep
