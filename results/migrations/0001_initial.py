# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('name', models.CharField(max_length=60)),
                ('category', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Mathlete',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('mao_id', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('answer', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('givenanswer', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('region', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('division', models.CharField(max_length=30)),
                ('mathletes', models.ManyToManyField(to='results.Mathlete')),
                ('school', models.ForeignKey(to='results.School')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('division', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='TestPaper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('place', models.IntegerField()),
                ('mathlete', models.ForeignKey(to='results.Mathlete')),
                ('school', models.ForeignKey(to='results.School')),
            ],
        ),
        migrations.CreateModel(
            name='TopicTest',
            fields=[
                ('test_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='results.Test')),
                ('topic', models.CharField(max_length=30)),
            ],
            bases=('results.test',),
        ),
        migrations.AddField(
            model_name='testpaper',
            name='test',
            field=models.ForeignKey(to='results.Test'),
        ),
        migrations.AddField(
            model_name='test',
            name='competition',
            field=models.ForeignKey(to='results.Competition'),
        ),
        migrations.AddField(
            model_name='questionanswer',
            name='paper',
            field=models.ForeignKey(to='results.TestPaper'),
        ),
        migrations.AddField(
            model_name='questionanswer',
            name='question',
            field=models.ForeignKey(to='results.Question'),
        ),
        migrations.AddField(
            model_name='question',
            name='test',
            field=models.ForeignKey(to='results.Test'),
        ),
    ]
