from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
import os
from main.utils import get_avatar
from .models import Book

MEDIA_FOLDER = os.path.join(settings.MEDIA_ROOT, 'books')


@login_required
def index(request):
    books = get_books(request.user)
    return render(request, 'books/index.html', {'books': books, 'avatar': get_avatar(request)})


def get_books(user):
    values = ['title', 'author', 'epub_id', 'created_at']
    books = user.books.all().values(*values).order_by('created_at')
    covers = set()
    for b in books:
        b['cover_filename'] = f'{b["title"]} - {b["author"]}.jpg'.replace(' ', '_')
        covers.add(b['cover_filename'])
    clean_up_media_folder(covers)
    return books


def clean_up_media_folder(covers):
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)
    for cover in os.listdir(MEDIA_FOLDER):
        if cover not in covers:
            os.remove(os.path.join(MEDIA_FOLDER, cover))


def upload_cover(request):
    user = request.user
    message = ''
    if request.method == 'POST':
        cover = request.FILES.get('cover')
        drive_url = request.POST.get('drive_url')
        title, author = cover.name.split('.')[0].split(' - ')
        epub_id = drive_url.split('/')[5]  # just the GDrive id of the file
        if user.books.filter(epub_id=epub_id).exists():
            message = 'Book is already in library!'
        else:
            save_new_book(user=user, title=title, author=author, epub_id=epub_id, cover=cover)
    return render(request, 'books/main.html', {'books': get_books(user), 'message': message})


def save_new_book(user, title, author, epub_id, cover):
    # Save new book to database
    new_book = Book(user=user, title=title, author=author, epub_id=epub_id)
    new_book.save()

    # Save book cover to media folder
    cover_file = os.path.join(MEDIA_FOLDER, cover.name.replace(' ', '_'))
    with open(cover_file, 'wb') as f:
        for chunk in cover.chunks():
            f.write(chunk)
