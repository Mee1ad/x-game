from django.contrib.auth.models import AbstractUser
from django_mysql.models import Model
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=127, null=True, unique=True)
    email = models.CharField(max_length=127, null=True)
    password = models.CharField(max_length=127)
    phone = models.CharField(max_length=15, null=True, unique=True)
    console = models.CharField(max_length=127, null=True)

