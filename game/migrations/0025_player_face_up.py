# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-05 02:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0024_game_card_face'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='face_up',
            field=models.BooleanField(default=False),
        ),
    ]
