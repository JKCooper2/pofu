# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 05:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_remove_player_hand'),
        ('cards', '0006_auto_20160801_0524'),
    ]

    operations = [
        migrations.AddField(
            model_name='hand',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='game.Player'),
        ),
    ]
