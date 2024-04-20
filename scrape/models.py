from django.db import models
from django.contrib.auth.models import User


class Keyword(models.Model):
    keyword = models.CharField(max_length=200)
    objects = models.Manager()

    def __str__(self):
        return str(self.keyword)


class Kleinanzeigen(Keyword):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kleinanzeigen')
    price = models.IntegerField(null=True)
    distance = models.IntegerField()
    latest_id = models.BigIntegerField(default=0)


class Urlaubspiraten(Keyword):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='urlaubspiraten')
    latest_datetime = models.DateTimeField(default=None, null=True)
