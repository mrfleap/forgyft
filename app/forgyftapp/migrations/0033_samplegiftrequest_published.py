# Generated by Django 2.1.2 on 2019-02-05 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forgyftapp', '0032_samplegiftidea'),
    ]

    operations = [
        migrations.AddField(
            model_name='samplegiftrequest',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]
