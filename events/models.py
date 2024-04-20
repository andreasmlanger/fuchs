from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    website = models.CharField(max_length=20, default='eventbrite')
    date = models.DateField()
    event = models.CharField(max_length=300)
    location = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    latitude = models.FloatField(default=None, null=True)
    longitude = models.FloatField(default=None, null=True)
    group = models.CharField(max_length=300)  # Meetup group
    attending = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.event)


class BlackList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklist')
    name = models.CharField(max_length=300)
    type = models.IntegerField()  # 0: event, 1: location, 2: group
    objects = models.Manager()

    def __str__(self):
        return str(self.name)
