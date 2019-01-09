# Generated by Django 2.1.5 on 2019-01-08 14:59

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0019_auto_20190108_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='access_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 18, 14, 59, 36, 795618, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='token',
            name='refresh_token_expire',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 7, 14, 59, 36, 795618, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='usertemp',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 8, 14, 59, 36, 795618, tzinfo=utc)),
        ),
    ]