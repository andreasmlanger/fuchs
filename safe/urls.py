from django.urls import path
from . import views

urlpatterns = [path('safe', views.index, name='safe'),
               path('add_message', views.add_message, name='add_message')]
