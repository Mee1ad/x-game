# Generated by Django 2.1.5 on 2019-01-30 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0014_auto_20190128_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='document',
            field=models.FileField(default='def', upload_to='documents/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='media',
            name='image',
            field=models.ImageField(default='defff', upload_to='image/'),
            preserve_default=False,
        ),
    ]