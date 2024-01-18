from django.contrib import admin
from .models import Message, Secret

admin.site.register(Message)
admin.site.register(Secret)
