# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 14:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20171003_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.CharField(max_length=20),
        ),
    ]
