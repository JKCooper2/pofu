# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 00:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0003_hand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hand',
            name='cards',
            field=models.ManyToManyField(blank=True, to='cards.Card'),
        ),
    ]