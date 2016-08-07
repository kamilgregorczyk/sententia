# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-16 20:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Pytanie')),
                ('help_text', models.CharField(blank=True, max_length=255, null=True, verbose_name='Pod tytu\u0142')),
                ('required', models.BooleanField(default=True, verbose_name='Wymagane')),
                ('order', models.PositiveIntegerField(default=0)),
                ('type', models.CharField(choices=[('singlechoice', 'Jednokrotnego wyboru'), ('multichoice', 'Wielokrotnego wyboru'), ('textarea', 'Pole tekstowe'), ('scale', 'skala')], max_length=255, verbose_name='Typ pytania')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_types', to='poll.Poll')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Typ pytania',
                'verbose_name_plural': 'Typy pytan',
            },
        ),
    ]
