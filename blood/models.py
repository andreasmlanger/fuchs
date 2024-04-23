from django.db import models
from django.contrib.auth.models import User


class Blood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blood')
    systolic = models.IntegerField()  # upper number
    diastolic = models.IntegerField()  # lower number
    pulse = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.systolic) + ' | ' + str(self.diastolic) + ' | ' + str(self.pulse)
