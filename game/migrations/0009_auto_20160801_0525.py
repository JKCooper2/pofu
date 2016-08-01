# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 05:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_player_hand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='player',
            name='hand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.Hand'),
        ),
    ]
