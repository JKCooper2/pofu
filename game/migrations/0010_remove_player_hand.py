# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 05:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_auto_20160801_0525'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='hand',
        ),
    ]
