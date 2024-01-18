from django.urls import path
from . import views

urlpatterns = [path('cookbook', views.index, name='cookbook'),
               path('cookbook/<str:url>', views.index, name='cookbook')]
