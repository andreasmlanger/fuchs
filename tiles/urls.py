from django.urls import path
from . import views

urlpatterns = [path('tiles', views.index, name='tiles')]
