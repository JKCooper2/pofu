# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-02 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0016_auto_20160802_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='cards',
            field=models.ManyToManyField(to='cards.Card'),
        ),
    ]
