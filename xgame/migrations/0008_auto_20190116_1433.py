# Generated by Django 2.1.5 on 2019-01-16 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0007_media_media_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='genres',
            new_name='genre',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='platforms',
            new_name='platform',
        ),
    ]