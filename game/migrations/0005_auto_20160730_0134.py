# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-30 01:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20160730_0058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invitation',
            old_name='to_user',
            new_name='user',
        ),
    ]
