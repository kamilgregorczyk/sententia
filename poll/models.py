# coding=utf-8
from __future__ import unicode_literals

import random
import string
import uuid
from collections import Counter
from threading import Thread

from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.utils import timezone


class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.SET_NULL, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.SET_NULL, editable=False,
                                   verbose_name=u"Autor")

    class Meta:
        abstract = True


def gen_code(len=3):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(len))


def get_code(cls, filter_params={}):
    code = gen_code()
    i = 0
    while cls.objects.filter(**filter_params).filter(code=code).exists():
        i += 1
        code = gen_code() if i < 1000 else gen_code(3 + (i / 1000))
    return code


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
    code = models.CharField(u"Klucz", max_length=255, db_index=True, unique=True)
    status = models.IntegerField(u"Status", choices=STATUS_CHOICES, default=0)
    list_status = models.IntegerField(u"Widoczna na stronie głównej", choices=STATUS_CHOICES, default=0)
    auth = models.IntegerField(u"Typ autoryzacji", choices=AUTH_CHOICES, default=0)
    allowed_users = models.ManyToManyField(User, verbose_name=u"Osoby które mogą zobaczyć i edytować ankietę",
                                           blank=True)
    allowed_groups = models.ManyToManyField(Group, verbose_name=u"Grupy które mogą zobaczyć i edytować ankietę",
                                            blank=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_code(Poll)
        return super(Poll, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Ankieta'
        verbose_name_plural = u'Ankiety'
        ordering = ['status', '-created_at']

    def get_absolute_url(self):
        return reverse("poll", kwargs={"poll_code": self.code})

    def get_results_count(self):
        return self.votes.all().values_list('form_id').distinct().count()

    def _save_results(self, context, token):
        form_id = uuid.uuid4()
        with transaction.atomic():
            for index, field in enumerate(context["formset"].cleaned_data):
                if isinstance(field['choice'], type([])):
                    Vote(value=', '.join(field['choice']), form_id=form_id, question=self.questions.all()[index],
                         poll=self).save()
                else:
                    Vote(value=field['choice'], form_id=form_id, question=self.questions.all()[index],
                         poll=self).save()

            if token:
                token.voted = True
                token.save(update_fields=["voted"])
        cache.delete(reverse('results', args=[self.id]))
        cache.delete("%s:template" % reverse('results', args=[self.id]))
        cache.delete("%s:template" % reverse('results_excel', args=[self.id]))

    def save_results(self, context, token):
        save_thread = Thread(target=self._save_results, args=(context, token,))
        save_thread.start()

    get_results_count.short_description = u"Wypełnień"


class Token(models.Model):
    poll = models.ForeignKey(Poll, related_name="tokens")
    code = models.CharField(u"Kod", max_length=255, unique=True)
    voted = models.BooleanField(u"Użyto?", default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_code(Token, {"poll": self.poll})
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

    def mode(self):
        values = self.votes.values_list('value', flat=True)
        return Counter(values).most_common(1)[0][0]

    def avg(self):
        try:
            values = self.votes.values_list('value', flat=True)
            values = map(int, values)
            return sum(values) / float(len(values))
        except (ZeroDivisionError, ValueError):
            return 0.0

    def median(self):
        values = self.votes.values_list('value', flat=True)
        return sorted(values)[len(values) // 2]

    def multiscale_results(self):
        values = self.votes.values_list('value', flat=True)
        values = map(lambda x: x.split(', '), values)
        values = [map(int, i) for i in values]

        return zip(*values)

    def arrayToDataTable(self):
        values = self.votes.values_list('value', flat=True)
        return Counter(values).items()


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
