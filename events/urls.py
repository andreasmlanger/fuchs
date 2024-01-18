from django.urls import path
from . import views

urlpatterns = [path('events', views.index, name='events'),
               path('refresh_events_grid', views.refresh_events_grid, name='refresh_events_grid')]
