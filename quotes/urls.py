from django.urls import path
from . import views

urlpatterns = [path('quotes', views.index, name='quotes'),
               path('add_quote', views.add_quote, name='add_quote')]
