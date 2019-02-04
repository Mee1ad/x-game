# Generated by Django 2.1.5 on 2019-01-30 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0015_auto_20190130_1214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='document',
        ),
        migrations.RemoveField(
            model_name='media',
            name='image',
        ),
        migrations.AddField(
            model_name='media',
            name='cover',
            field=models.FileField(default='sfasf', upload_to='cover/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='media',
            name='screenshot',
            field=models.ImageField(default='fhhft', upload_to='screenshot/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='media',
            name='seller_photos',
            field=models.ImageField(default='fddfvD', upload_to='seller_photos/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='media',
            name='trailer',
            field=models.ImageField(default='sfsfs', upload_to='trailer/'),
            preserve_default=False,
        ),
    ]