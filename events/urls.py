from django.urls import path
from . import views

urlpatterns = [path('events', views.index, name='events'),
               path('events_muc', views.events_muc, name='events_muc'),
               path('refresh_events_grid', views.refresh_events_grid, name='refresh_events_grid')]
