from django.contrib.auth.models import AbstractUser
from django_mysql.models import ListCharField
from django_mysql.models import Model
from django.db import models


class Game(Model):
    igdb_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    popularity = models.FloatField(blank=True)
    total_rating = models.FloatField(null=True, blank=True)
    total_rating_count = models.IntegerField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    collection = models.CharField(max_length=255, null=True, blank=True)
    first_release_date = models.BigIntegerField(null=True, blank=True)
    hypes = models.IntegerField(null=True, blank=True)
    perspective = models.CharField(max_length=255, null=True, blank=True)
    alternative_names = ListCharField(
        base_field=models.CharField(max_length=255),
        size=10,
        max_length=(10 * 256))
    platforms = ListCharField(
        base_field=models.CharField(max_length=7),
        size=20,
        max_length=(20 * 8))
    genres = ListCharField(
        base_field=models.CharField(max_length=255),
        size=10,
        max_length=(10 * 256))
    theme = ListCharField(
        base_field=models.CharField(max_length=127),
        size=10,
        max_length=(10 * 128))
    publisher = ListCharField(
        base_field=models.CharField(max_length=255),
        size=10,
        max_length=(10 * 256))
    developer = ListCharField(
        base_field=models.CharField(max_length=255),
        size=10,
        max_length=(10 * 256))


class User(AbstractUser):
    phone = models.CharField(max_length=15)
    device_id = models.CharField(max_length=127)
    platform = models.SmallIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    address = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    activation_code = models.CharField(max_length=7, null=True, blank=True)
    activation_expire = models.DateTimeField(auto_now_add=True)
    access_token = models.TextField(max_length=1023, null=True, blank=True)
    refresh_token = models.TextField(max_length=1023, null=True, blank=True)
    access_token_expire = models.DateTimeField(auto_now_add=True)
    refresh_token_expire = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Seller(Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    platform = models.SmallIntegerField()
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255)
    new = models.BooleanField(default=False)
    price = models.IntegerField()
    sold = models.BooleanField(default=False)
    trends = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Media(Model):
    table_id = models.IntegerField()
    description = models.TextField()
    type = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    text = models.TextField()
    rate = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
