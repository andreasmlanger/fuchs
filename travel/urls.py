from django.urls import path
from . import views

urlpatterns = [path('travel', views.index, name='travel'),
               path('travel/<str:keyword>', views.index, name='travel')]
