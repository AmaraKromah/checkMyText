# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-08 01:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20170607_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfile',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userfile',
            name='word_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]