# Generated by Django 2.1.2 on 2019-01-31 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0004_auto_20190113_0431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapeproduct',
            name='image_url',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='scrapeproduct',
            name='url',
            field=models.URLField(),
        ),
    ]
