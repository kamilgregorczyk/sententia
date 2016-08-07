# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0027_poll_list_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='auth',
            field=models.IntegerField(choices=[(0, 'Ukryta'), (1, 'Publikowana')], default=0, verbose_name='Typ autoryzacji'),
        ),
    ]
