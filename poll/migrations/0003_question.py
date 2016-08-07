# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-16 20:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('poll', '0002_questiontype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('title', models.CharField(max_length=255, verbose_name='Odpowied\u017a')),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('question_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='poll.QuestionType')),
                ('updated_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Odpowied\u017a',
                'verbose_name_plural': 'Odpowied\u017a',
            },
        ),
    ]
