# Generated by Django 2.1.5 on 2019-01-30 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0018_auto_20190130_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='igdb_id',
        ),
        migrations.AlterField(
            model_name='game',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]