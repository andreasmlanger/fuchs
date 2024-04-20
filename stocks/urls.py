from django.urls import path
from . import views

urlpatterns = [path('portfolio', views.portfolio, name='portfolio'),
               path('watchlist', views.watchlist, name='watchlist'),
               ]
