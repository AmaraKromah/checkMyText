# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-22 14:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20170622_1610'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rating',
            old_name='user',
            new_name='user_file',
        ),
    ]
