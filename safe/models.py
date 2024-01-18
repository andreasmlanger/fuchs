from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import base64


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.user) + ' | ' + str(self.created_at)


class EncryptedField(models.TextField):
    def __init__(self, *args, **kwargs):
        secret_key = settings.SECRET_KEY.encode()  # key must be 32 bytes
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(secret_key))
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.cipher_suite.decrypt(value.encode()).decode()

    def to_python(self, value):
        if value is None:
            return value
        return self.cipher_suite.decrypt(value.encode()).decode()

    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher_suite.encrypt(value.encode()).decode()


class Secret(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='secrets')
    text = EncryptedField()  # secret key is used for encryption!
    objects = models.Manager()

    def __str__(self):
        return f'Secret of {self.user}'
