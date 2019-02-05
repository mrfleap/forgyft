# Generated by Django 2.1.2 on 2019-02-05 04:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forgyftapp', '0034_user_expert_requests'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='expert_requests',
        ),
        migrations.AddField(
            model_name='gifteeprofile',
            name='expert',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expert', to=settings.AUTH_USER_MODEL),
        ),
    ]
