# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-07 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_userfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfile',
            name='file',
            field=models.FileField(blank=True, upload_to=b''),
        ),
    ]