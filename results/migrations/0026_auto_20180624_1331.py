# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-06-24 18:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0025_auto_20180113_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='answers_tdid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='test',
            name='solns_tdid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='test',
            name='test_tdid',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
