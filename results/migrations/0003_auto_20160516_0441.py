# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-16 04:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0002_auto_20160516_0426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testpaper',
            name='blank',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='testpaper',
            name='first_wrong',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='testpaper',
            name='place',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='testpaper',
            name='right',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='testpaper',
            name='score',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='testpaper',
            name='wrong',
            field=models.IntegerField(blank=True),
        ),
    ]
