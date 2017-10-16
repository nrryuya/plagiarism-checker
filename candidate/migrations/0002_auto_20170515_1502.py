# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-15 06:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='cover',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='doc_sim',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='judged_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='url',
            field=models.URLField(max_length=1000),
        ),
    ]
