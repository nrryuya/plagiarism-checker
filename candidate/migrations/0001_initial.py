# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-21 00:42
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rss', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=255, verbose_name='タイトル')),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('judged_at', models.DateTimeField(default=datetime.datetime.now)),
                ('doc_sim', models.FloatField()),
                ('cover', models.FloatField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rss.Article')),
            ],
            options={
                'db_table': 'candidates',
            },
        ),
        migrations.CreateModel(
            name='Sim_part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('original_part', models.TextField()),
                ('imitated_part', models.TextField()),
                ('sim_score', models.FloatField()),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.Candidate')),
            ],
            options={
                'db_table': 'sim_parts',
            },
        ),
    ]