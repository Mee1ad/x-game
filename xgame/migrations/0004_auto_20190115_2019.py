# Generated by Django 2.1.5 on 2019-01-15 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0003_auto_20190115_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='platform',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]