# Generated by Django 2.1.5 on 2019-01-08 12:56

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0013_auto_20190108_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='access_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 18, 12, 56, 30, 197250, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='token',
            name='refresh_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 7, 12, 56, 30, 197250, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='usertemp',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 8, 12, 56, 30, 197250, tzinfo=utc)),
        ),
    ]