# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-05 01:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0023_auto_20160805_0102'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='card_face',
            field=models.IntegerField(default=2),
        ),
    ]
