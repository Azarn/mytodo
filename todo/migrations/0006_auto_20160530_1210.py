# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 12:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_auto_20160530_0902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='deadline',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
