# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-25 21:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_auto_20170622_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='stars',
            field=models.FloatField(),
        ),
    ]
