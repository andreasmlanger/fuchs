from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.BinaryField(max_length=None)
    city = models.CharField(max_length=200, default='')
    objects = models.Manager()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    app = models.CharField(max_length=20)  # name of the app
    due = models.DateTimeField(auto_now_add=True)  # time of next email notification
    email = models.BooleanField(default=False)  # boolean if emails should be sent out
    objects = models.Manager()

    def __str__(self):
        return str(self.app) + ' - next: ' + str(self.due)[:19]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Notification.objects.create(user=instance, app='events')
        Notification.objects.create(user=instance, app='quotes')
        Notification.objects.create(user=instance, app='scrape')
        Notification.objects.create(user=instance, app='stocks')
        Notification.objects.create(user=instance, app='vocabulary')


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(pre_save, sender=User)
def normalize_city_name(sender, instance, **kwargs):
    try:
        if instance.profile.city.lower() in ["munich", "muenchen"]:
            instance.profile.city = "München"
    except ObjectDoesNotExist:
        pass  # needed when superuser is created in console and profile does not yet exist
