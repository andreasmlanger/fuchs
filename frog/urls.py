from django.urls import path
from . import views

urlpatterns = [path('frog', views.index, name='frog')]
