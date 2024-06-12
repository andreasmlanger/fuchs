from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from main.utils import decode_bytes, get_avatar, uploaded_image_to_base64
from .models import Book


@login_required
def index(request):
    if request.method == 'POST' and request.POST.get('task') == 'remove':
        request.user.books.get(epub_id=request.POST.get('epub_id')).delete()
        return JsonResponse({})
    books = get_books(request.user)
    return render(request, 'books/index.html', {'books': books, 'avatar': get_avatar(request)})


def get_books(user):
    values = ['title', 'author', 'epub_id', 'cover_image', 'created_at']
    books = user.books.all().values(*values).order_by('created_at')
    for b in books:
        b['cover_image'] = decode_bytes(b['cover_image'])
    return books


def upload_cover(request):
    user = request.user
    message = ''
    if request.method == 'POST':
        cover = request.FILES.get('cover')
        cover_image = uploaded_image_to_base64(cover, w=200, h=300)  # 1.5X aspect ratio
        drive_url = request.POST.get('drive_url')
        title, author = cover.name.split('.')[0].split(' - ')
        epub_id = drive_url.split('/')[5]  # just the GDrive id of the file
        if user.books.filter(epub_id=epub_id).exists():
            message = 'Book is already in library!'
        else:
            Book(user=user, title=title, author=author, epub_id=epub_id, cover_image=cover_image).save()
    return render(request, 'books/main.html', {'books': get_books(user), 'message': message})
