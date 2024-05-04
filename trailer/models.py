from django.db import models
from django.contrib.auth.models import User


class Trailer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trailer')
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    img_url = models.CharField(max_length=400)
    muted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.title)
