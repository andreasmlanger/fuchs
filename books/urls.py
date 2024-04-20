from django.urls import path
from . import views

urlpatterns = [path('books', views.index, name='books'),
               path('upload_cover', views.upload_cover, name='upload_cover')]
