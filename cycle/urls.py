from django.urls import path
from . import views

urlpatterns = [path('cycle', views.cycle, name='cycle'),
               path('cycle/<str:route_id>/', views.open_route, name='open_route'),
               ]
