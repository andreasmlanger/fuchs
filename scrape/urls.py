from django.urls import path
from . import views

urlpatterns = [path('scrape', views.index, name='scrape'),
               path('add_keyword', views.add_keyword, name='add_keyword')
               ]
