from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta


class Vocab(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vocabulary')
    due = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField(default=0)
    language = models.CharField(max_length=2, default='en')
    word_1 = models.CharField(max_length=200)  # word in foreign language
    word_2 = models.CharField(max_length=200)  # word in native language
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.word_1)

    def delay_due(self):
        self.due += timedelta(hours=1)  # new words can only be studied after a delay
        self.save()

    def save(self, *args, **kwargs):
        created = self.pk is None
        super(Vocab, self).save(*args, **kwargs)
        if created and self.language == 'pt':
            PortugueseVerb.objects.create(user=self.user, vocab=self)


class PortugueseVerb(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vocab = models.ForeignKey(Vocab, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    present_eu = models.CharField(max_length=50, default=None, null=True)
    present_ele = models.CharField(max_length=50, default=None, null=True)
    present_nos = models.CharField(max_length=50, default=None, null=True)
    present_eles = models.CharField(max_length=50, default=None, null=True)
    preterite_eu = models.CharField(max_length=50, default=None, null=True)
    preterite_ele = models.CharField(max_length=50, default=None, null=True)
    preterite_nos = models.CharField(max_length=50, default=None, null=True)
    preterite_eles = models.CharField(max_length=50, default=None, null=True)
    imperfect_eu = models.CharField(max_length=50, default=None, null=True)
    imperfect_ele = models.CharField(max_length=50, default=None, null=True)
    imperfect_nos = models.CharField(max_length=50, default=None, null=True)
    imperfect_eles = models.CharField(max_length=50, default=None, null=True)
    future_eu = models.CharField(max_length=50, default=None, null=True)
    future_ele = models.CharField(max_length=50, default=None, null=True)
    future_nos = models.CharField(max_length=50, default=None, null=True)
    future_eles = models.CharField(max_length=50, default=None, null=True)
    conditional_eu = models.CharField(max_length=50, default=None, null=True)
    conditional_ele = models.CharField(max_length=50, default=None, null=True)
    conditional_nos = models.CharField(max_length=50, default=None, null=True)
    conditional_eles = models.CharField(max_length=50, default=None, null=True)
    subjunctive_eu = models.CharField(max_length=50, default=None, null=True)
    subjunctive_ele = models.CharField(max_length=50, default=None, null=True)
    subjunctive_nos = models.CharField(max_length=50, default=None, null=True)
    subjunctive_eles = models.CharField(max_length=50, default=None, null=True)
    past_participle = models.CharField(max_length=50, default=None, null=True)
    gerund = models.CharField(max_length=50, default=None, null=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.vocab)
