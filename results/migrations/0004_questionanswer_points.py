# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-16 04:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_auto_20160516_0441'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswer',
            name='points',
            field=models.IntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]
