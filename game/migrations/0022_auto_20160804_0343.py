# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-04 03:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0021_auto_20160804_0336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='action',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='game.Action'),
        ),
    ]
