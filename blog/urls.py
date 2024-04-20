from django.urls import path
from . import views

urlpatterns = [path('blog', views.index, name='blog'),
               path('blog/<str:blog_id>/', views.open_single_post, name='open_single_post')]
