from django.db import models
from django.contrib.auth.models import User


class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stocks')
    in_portfolio = models.BooleanField(default=False)
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    order_date = models.DateTimeField(default=None, null=True)
    order_price = models.FloatField(default=None, null=True)
    volume = models.IntegerField(default=None, null=True)
    buy_recommendation = models.BooleanField(default=False)
    today = models.FloatField(default=0.0)
    objects = models.Manager()

    def __str__(self):
        return str(self.name) + ' [' + str(self.symbol) + ']'
