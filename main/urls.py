from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [path('', views.home, name='home'),
               path('account', views.account, name='account'),
               path('scheduler/<int:job>', views.scheduler, name='scheduler'),
               path('weather', views.weather, name='weather'),
               path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico')))
               ]
