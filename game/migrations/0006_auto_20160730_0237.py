# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-30 02:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20160730_0134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='title',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]