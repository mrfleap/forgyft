# Generated by Django 2.1.2 on 2018-12-09 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forgyftapp', '0017_auto_20181209_0653'),
    ]

    operations = [
        migrations.AddField(
            model_name='gifteeprofile',
            name='_slug',
            field=models.SlugField(blank=True, max_length=7),
        ),
    ]
