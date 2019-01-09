# Generated by Django 2.1.5 on 2019-01-08 10:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0007_auto_20190108_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='access_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 18, 10, 24, 25, 483970, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='token',
            name='refresh_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 7, 10, 24, 25, 483970, tzinfo=utc)),
        ),
    ]
