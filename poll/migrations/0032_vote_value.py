# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 18:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0031_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='value',
            field=models.CharField(default=None, max_length=255, verbose_name='Kod'),
            preserve_default=False,
        ),
    ]
