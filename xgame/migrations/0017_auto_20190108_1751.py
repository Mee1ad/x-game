# Generated by Django 2.1.5 on 2019-01-08 14:21

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0016_auto_20190108_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='access_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 18, 14, 21, 52, 113493, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='token',
            name='refresh_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 7, 14, 21, 52, 113493, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='usertemp',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 8, 14, 21, 52, 113493, tzinfo=utc)),
        ),
    ]