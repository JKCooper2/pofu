# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-04 02:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0018_auto_20160804_0231'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='error',
            field=models.CharField(default='', max_length=100),
        ),
    ]
