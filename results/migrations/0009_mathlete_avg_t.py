# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-19 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0008_testpaper_t_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='mathlete',
            name='avg_t',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
