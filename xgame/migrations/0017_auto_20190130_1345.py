# Generated by Django 2.1.5 on 2019-01-30 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xgame', '0016_auto_20190130_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='cover',
            field=models.ImageField(upload_to='cover/'),
        ),
        migrations.AlterField(
            model_name='media',
            name='trailer',
            field=models.FilePathField(),
        ),
    ]
