# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-30 03:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20160730_0237'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='points',
            field=models.IntegerField(default=0),
        ),
    ]
