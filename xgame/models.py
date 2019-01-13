from django.contrib.auth.models import AbstractUser
from django_mysql.models import ListCharField
from django_mysql.models import Model
from django.utils import timezone
from django.db import models


class Platform(Model):
    igdb_id = models.CharField(max_length=127, null=True)
    name = models.CharField(max_length=255)


class User(AbstractUser):
    phone = models.CharField(max_length=15, null=True, unique=True)
    device_id = models.CharField(max_length=127, null=True)
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True)


class UserTemp(Model):
    phone = models.CharField(max_length=15)
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


class Genre(Model):
    igdb_id = models.CharField(max_length=127, null=True)
    name = models.CharField(max_length=255)


class Theme(Model):
    igdb_id = models.CharField(max_length=127)
    name = models.CharField(max_length=255)


class Company(Model):
    igdb_id = models.CharField(max_length=127, null=True)
    name = models.CharField(max_length=255)
    publisher = models.BooleanField(default=False)
    developer = models.BooleanField(default=False)


class Game(Model):
    igdb_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    collection = models.CharField(max_length=255, null=True, blank=True)
    cover = models.CharField(max_length=127)
    first_release_date = models.BigIntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    theme = models.ManyToManyField(Theme)
    hypes = models.IntegerField(null=True, blank=True)
    company = models.ManyToManyField(Company)
    platforms = models.ManyToManyField(Platform)
    popularity = models.FloatField()
    total_rating = models.FloatField(null=True, blank=True)
    total_rating_count = models.IntegerField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)


class Collection(Model):
    igdb_id = models.CharField(max_length=127, null=True)
    name = models.CharField(max_length=255)


class GameName(Model):
    igdb_id = models.CharField(max_length=127, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, blank=True)


class Cover(Model):
    igdb_id = models.CharField(max_length=127)
    image_id = models.CharField(max_length=127, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True, related_name='game_cover')


class ScreenShot(Model):
    igdb_id = models.CharField(max_length=127)
    image_id = models.CharField(max_length=127, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)


class Videos(Model):
    igdb_id = models.CharField(max_length=127)
    video_id = models.CharField(max_length=127, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)


class Comment(Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    text = models.TextField()


class Info(Model):
    version = models
    min_version = models
    version_info = models




