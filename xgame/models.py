from django.contrib.auth.models import AbstractUser
from django_mysql.models import Model
from django.utils import timezone
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=127, null=True, unique=True)
    email = models.CharField(max_length=127, null=True)
    phone = models.CharField(max_length=15, null=True, unique=True)
    console = models.CharField(max_length=127, null=True)
    device_id = models.CharField(max_length=127, null=True)


class UserTemp(Model):
    phone = models.CharField(max_length=15, unique=True)
    activation_code = models.CharField(max_length=7)
    device_id = models.CharField(max_length=127, null=True)
    expire_date = models.DateTimeField(default=timezone.now)


class Token(Model):
    def __str__(self):
        self.data = '{'+'"accessToken": "'+self.access_token+'", "refreshToken": "'+self.refresh_token+'"}'
        return self.data

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.TextField(max_length=1023)
    refresh_token = models.TextField(max_length=1023)
    access_token_expire = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=10))
    refresh_token_expire = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=30))




