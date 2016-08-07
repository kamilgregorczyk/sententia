# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-16 23:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('poll', '0012_auto_20160717_0130'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='allowed_users',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='allowed_users', to=settings.AUTH_USER_MODEL, verbose_name='Osoby kt\xf3re mog\u0105 zobaczy\u0107 i edytowa\u0107 ankiet\u0119'),
            preserve_default=False,
        ),
    ]
