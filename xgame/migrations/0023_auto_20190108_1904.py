# Generated by Django 2.1.5 on 2019-01-08 15:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0022_auto_20190108_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='access_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 18, 15, 34, 20, 714986, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='token',
            name='refresh_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 7, 15, 34, 20, 714986, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='usertemp',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 8, 15, 34, 20, 713987, tzinfo=utc)),
        ),
    ]
