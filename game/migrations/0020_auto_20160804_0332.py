# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-04 03:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0019_action_error'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='action',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='game.Action'),
        ),
    ]