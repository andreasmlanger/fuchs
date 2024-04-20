from django.urls import path
from . import views

urlpatterns = [path('trailer', views.index, name='trailer')]
