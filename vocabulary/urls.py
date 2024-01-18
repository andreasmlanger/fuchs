from django.urls import path
from . import views

urlpatterns = [path('vocabulary', views.index, name='vocabulary'),
               path('vocabulary/study', views.study, name='study'),
               path('vocabulary/new', views.new, name='new'),
               path('vocabulary/words', views.words, name='words'),
               path('vocabulary/verbs', views.verbs, name='verbs')
               ]
