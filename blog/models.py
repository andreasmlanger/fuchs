from django.db import models


class Data(models.Model):
    updated_at_remote = models.DateTimeField(auto_now_add=True)  # time of last Airtable update (remote)
    updated_at_local = models.DateTimeField(auto_now_add=True)  # time of last Airtable update (local)
    objects = models.Manager()
