# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-17 21:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0011_school_id_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='testpaper',
            name='s_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
