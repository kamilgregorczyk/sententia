# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-16 23:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0010_token_voted_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='voted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
