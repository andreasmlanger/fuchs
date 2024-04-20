from django.db import models
from django.contrib.auth.models import User


class Quote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotes')
    quote = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.quote)
