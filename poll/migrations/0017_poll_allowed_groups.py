# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-17 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('poll', '0016_auto_20160717_0222'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='allowed_groups',
            field=models.ManyToManyField(blank=True, to='auth.Group', verbose_name='Grupy kt\xf3re mog\u0105 zobaczy\u0107 i edytowa\u0107 ankiet\u0119'),
        ),
    ]
