# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 06:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0008_auto_20160801_0548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hand',
            name='player',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='game.Player'),
        ),
    ]
