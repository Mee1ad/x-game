# Generated by Django 2.1.5 on 2019-01-08 09:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0002_auto_20190108_1329'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='refresh_token_token_expire',
        ),
        migrations.AddField(
            model_name='token',
            name='refresh_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 7, 13, 29, 56, 232507)),
        ),
        migrations.AlterField(
            model_name='token',
            name='access_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 18, 13, 29, 56, 232507)),
        ),
    ]
