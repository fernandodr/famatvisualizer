# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-16 04:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0005_auto_20160516_0445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testpaper',
            name='first_wrong',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
