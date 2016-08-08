# coding=utf-8
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import random
import string

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.SET_NULL, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.SET_NULL, editable=False, verbose_name=u"Autor")

    class Meta:
        abstract = True


def gen_code(len=3):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(len))


class Poll(BaseModel):
    STATUS_CHOICES = (
        (0, u'Ukryta'),
        (1, u'Publikowana'),
    )
    AUTH_CHOICES = (
        (0, u'Otwarta'),
        (1, u'Zabezpieczona kluczami (zakładka tokeny)'),
    )

    title = models.CharField(u"Tytuł", max_length=255)
    description = models.TextField(u"Opis", blank=True, null=True)
    code = models.CharField(u"Klucz", max_length=255, unique=True, db_index=True)
    status = models.IntegerField(u"Status", choices=STATUS_CHOICES, default=0)
    list_status = models.IntegerField(u"Widoczna na stronie głównej", choices=STATUS_CHOICES, default=0)
    auth = models.IntegerField(u"Typ autoryzacji", choices=AUTH_CHOICES, default=0)
    max_replies = models.IntegerField(u"Maksymalna liczba odpowiedzi", null=True, blank=True, help_text=u"Zostaw puste jeżeli ma być nieograniczona")
    allowed_users = models.ManyToManyField(User, verbose_name=u"Osoby które mogą zobaczyć i edytować ankietę", blank=True)
    allowed_groups = models.ManyToManyField(Group, verbose_name=u"Grupy które mogą zobaczyć i edytować ankietę", blank=True)




    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = gen_code()
            i = 0
            while Poll.objects.filter(code=self.code).exists():
                i += 1
                self.code = gen_code() if i < 37 else gen_code(3 + (i / 37))
        return super(Poll, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Ankieta'
        verbose_name_plural = u'Ankiety'
        ordering = ['status', '-created_at']

    def get_absolute_url(self):
        return reverse("poll", kwargs={"poll_code": self.code})


class Token(models.Model):
    poll = models.ForeignKey(Poll, related_name="tokens")
    code = models.CharField(u"Kod", max_length=255, unique=True)
    voted = models.BooleanField(u"Użyto?", default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = gen_code()
            i = 0
            while Token.objects.filter(poll=self.poll, code=self.code).exists():
                i += 1
                self.code = gen_code() if i < 37 else gen_code(3 + (i / 37))
        return super(Token, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s" % self.code

    class Meta:
        verbose_name = u'Token'
        verbose_name_plural = u'Tokeny'


class Question(models.Model):
    TYPE_CHOICES = (
        ('SingleChoice', u'Jednokrotnego wyboru'),
        ('MultiChoice', u'Wielokrotnego wyboru'),
        ('TextArea', u'Pole tekstowe'),
        ('Scale', u'Skala'),
        ('MultiScale', u'Skala wielowierszowa'),
    )
    poll = models.ForeignKey(Poll, related_name="questions")
    title = models.CharField(u"Pytanie", max_length=255)
    help_text = models.CharField(u"Pod tytuł", max_length=255, blank=True, null=True)
    required = models.BooleanField(u"Wymagane", default=True)
    order = models.PositiveIntegerField(default=0)
    type = models.CharField(u"Typ pytania", choices=TYPE_CHOICES, max_length=255, default='singlechoice')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = u'Pytanie'
        verbose_name_plural = u'Pytania'


def get_now():
    return timezone.localtime(timezone.now())


class Vote(models.Model):
    question = models.ForeignKey(Question, related_name="votes")
    poll = models.ForeignKey(Poll, related_name="votes")
    form_id = models.CharField(u"Kod", max_length=255)
    value = models.CharField(u"Wartość", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = u'Wybór'
        verbose_name_plural = u'Wybory'

    def __unicode__(self):
        return self.value


class Choice(models.Model):
    order = models.PositiveIntegerField(default=0)
    question_type = models.ForeignKey(Question, null=True, blank=True, related_name="choices")
    title = models.CharField(u"Wybór", max_length=255)

    class Meta:
        verbose_name = u'Odpowiedźi'
        verbose_name_plural = u'Odpowiedźi'
        ordering = ['order']

    def __unicode__(self):
        return self.title
