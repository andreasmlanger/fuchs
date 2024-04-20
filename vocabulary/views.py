from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from main.emails import send_email
from main.utils import get_avatar, update_notification
from .models import PortugueseVerb, Vocab
from .verbs import add_top_100_portuguese_verbs_to_vocabulary, check_if_is_verb, load_verbs
from .utils import *


@login_required
def index(request):
    return render(request, 'vocabulary/index.html', {'words': len(load_vocab(request.user, to_study=True)),
                                                     'avatar': get_avatar(request)})


@login_required
def study(request):
    if request.POST:
        if request.POST.get('task') == 'update_level':
            v = request.user.vocabulary.get(id=request.POST.get('id'))
            typed_word = request.POST.get('typed_word')
            delta_level = int(request.POST.get('delta_level'))
            if delta_level < 0 < len(request.user.vocabulary.filter(word_1=typed_word, word_2=v.word_2)):
                delta_level = 0  # don't lower level for a word that has an alternative translation
            v.level = max(0, v.level + delta_level)
            v.due = datetime.now() + WAITING_TIME[v.level]
            v.save()
            if v.language == 'pt':
                check_if_is_verb(v)
            return HttpResponse()
    update_notification(request.user, 'vocabulary', time_delta=timedelta(minutes=5))  # reset notification
    return render(request, 'vocabulary/study.html',
                  {'vocab': load_vocab(request.user, to_study=True), 'languages': get_languages(),
                   'avatar': get_avatar(request)})


def load_vocab(user, to_study=False):
    values = ['id', 'level', 'word_1', 'word_2', 'language']
    max_level = max(WAITING_TIME.keys())
    now = datetime.now()
    if to_study:
        vocab = user.vocabulary.filter(level__lt=max_level, due__lt=now).values(*values).order_by('?')  # shuffle
        vocab = alternate(vocab)
        vocab = vocab[:BATCH_SIZE]
    else:
        vocab = user.vocabulary.all().values(*values).order_by('-created_at')
    return list(vocab)


def alternate(vocab):
    for v in vocab:
        if v['level'] % 2:
            v['word_1'], v['word_2'] = v['word_2'], v['word_1']  # alternate between Foreign-German and German-Foreign
    return vocab


def vocab_ready_for_study(user):
    update_notification(user, 'vocabulary')
    return len(user.vocabulary.filter(level__lt=10, due__lt=datetime.now()))


@login_required
def new(request):
    if request.POST:
        v = Vocab(user=request.user, word_1=request.POST.get('word_1'), word_2=request.POST.get('word_2'),
                  language=request.POST.get('language'))
        v.save()
        v.delay_due()
        return HttpResponse()
    return render(request, 'vocabulary/new.html',
                  {'vocab': load_vocab(request.user), 'languages': get_languages(),
                   'default_language': LANGUAGES[0], 'avatar': get_avatar(request)})


@login_required
def words(request):
    if request.POST:
        if request.POST.get('task') == 'download':
            if request.POST.get('content') == 'top-100-pt-verbs':
                add_top_100_portuguese_verbs_to_vocabulary(request.user)
        elif request.POST.get('task') == 'delete':
            request.user.vocabulary.get(id=request.POST.get('id')).delete()
        elif request.POST.get('task') == 'edit':
            v = request.user.vocabulary.get(id=request.POST.get('id'))
            if request.POST.get('vocab') == '1':
                v.word_1 = request.POST.get('value')
            elif request.POST.get('vocab') == '2':
                v.word_2 = request.POST.get('value')
            v.save()
        return HttpResponse()
    return render(request, 'vocabulary/words.html',
                  {'vocab': load_vocab(request.user), 'languages': get_languages(),
                   'default_language': LANGUAGES[0], 'avatar': get_avatar(request)})


def send_vocab_notification_email(user):
    html = '<span>Check it out <a href="fuchs.onrender.com/vocabulary">here</a>!'
    send_email(user.email, 'New vocabulary to study!', html)
    update_notification(user, 'vocabulary', time_delta=timedelta(hours=24))  # allow 24 hours to study new vocab


@login_required
def verbs(request):
    if request.POST:
        if request.POST.get('task') == 'update_level':
            v = PortugueseVerb.objects.get(id=request.POST.get('id'))
            delta_level = int(request.POST.get('delta_level'))
            v.level = max(0, v.level + delta_level)
            v.save()
            return HttpResponse()
    return render(request, 'vocabulary/verbs.html',
                  {'verbs': load_verbs(request.user), 'amblyopia': 1 if request.GET.get('q', '') == 'amblyopia' else 0,
                   'avatar': get_avatar(request)})
