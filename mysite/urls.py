from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from registration import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('password_change/', views.password_change, name='change_password'),
    path('', include('django.contrib.auth.urls')),
    path('', include('main.urls')),
    path('', include('blog.urls')),
    path('', include('blood.urls')),
    path('', include('books.urls')),
    path('', include('cookbook.urls')),
    path('', include('cycle.urls')),
    path('', include('events.urls')),
    path('', include('frog.urls')),
    path('', include('quotes.urls')),
    path('', include('safe.urls')),
    path('', include('scrape.urls')),
    path('', include('stocks.urls')),
    path('', include('trailer.urls')),
    path('', include('travel.urls')),
    path('', include('vocabulary.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
