# coding=utf-8
import datetime
import locale
import time
import uuid

import xlwt
from django import forms
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http.response import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils import timezone

from poll.forms import BaseQuestionFormset
from poll.forms import SingleChoiceForm
from poll.models import Poll, Vote


def poll_start(request, poll_code, token=None):
    poll = get_object_or_404(Poll.objects.select_related('created_by'), code=poll_code, status=1)
    token_obj = None
    """Brak tokenu"""
    if poll.auth and not token:
        raise PermissionDenied
    """Token wykorzystany"""
    if token and poll.auth:
        token_obj = get_object_or_404(poll.tokens, code=token)
        if token_obj.voted:
            raise PermissionDenied
    return render(request, 'website/start.html', {'poll': poll, "token": token})


def poll_view(request, poll_code, token=None):
    poll = get_object_or_404(Poll.objects.prefetch_related('questions', 'tokens', 'questions__choices'), code=poll_code, status=1)
    token_obj = None
    """Brak tokenu"""
    if poll.auth and not token:
        raise PermissionDenied
    """Token wykorzystany"""
    if token and poll.auth:
        token_obj = get_object_or_404(poll.tokens, code=token)
        if token_obj.voted:
            raise PermissionDenied
    questions_count = poll.questions.count()
    QuestionFormset = forms.formset_factory(SingleChoiceForm, BaseQuestionFormset, extra=questions_count, validate_max=True, validate_min=True, min_num=questions_count,
                                            max_num=questions_count)
    if request.method == 'POST':
        formset = QuestionFormset(request.POST, request.FILES, form_kwargs={"questions": poll.questions.all()})
        if formset.is_valid():
            form_id = uuid.uuid4()
            with transaction.atomic():
                for index, field in enumerate(formset.cleaned_data):
                    if isinstance(field['choice'], type([])):
                        Vote(value=', '.join(field['choice']), form_id=form_id, question=poll.questions.all()[index], poll=poll).save()
                    else:
                        Vote(value=field['choice'], form_id=form_id, question=poll.questions.all()[index], poll=poll).save()

                next_values = {"poll_code": poll.code}
                if token_obj:
                    next_values.update({"token": token})
                    token_obj.voted = True
                    token_obj.save(update_fields=["voted"])
            return HttpResponseRedirect(reverse("poll_end", kwargs=next_values))
    else:
        formset = QuestionFormset(form_kwargs={"questions": poll.questions.all()})

    return render(request, 'website/poll.html', {'formset': formset, 'poll': poll})


def poll_end(request, poll_code, token=None):
    poll = get_object_or_404(Poll.objects.select_related('created_by'), code=poll_code, status=1)
    token_obj = None
    """Brak tokenu"""
    if poll.auth and not token:
        raise PermissionDenied
    return render(request, 'website/end.html', {'poll': poll})


def faq_view(request):
    return render(request, 'website/faq.html')


def index(request):
    return render(request, 'website/index.html', {"polls": Poll.objects.filter(status=1, auth=0, list_status=1)})


def results(request, object_id):
    table = []
    poll = Poll.objects.prefetch_related('questions', 'questions__choices', 'questions__votes', 'allowed_users', 'allowed_groups').get(id=object_id)
    if not (poll.created_by == request.user or request.user in poll.allowed_users.all() or request.user.id in poll.allowed_groups.values_list('user__id', flat=True)):
        raise PermissionDenied()
    form_ids = list(poll.votes.values_list('form_id', 'created_at').distinct('form_id'))
    form_ids.sort(key=lambda k: k[1], reverse=True)
    for form_id in form_ids:
        row = [timezone.localtime(form_id[1])]
        for question in poll.questions.all():
            try:
                vote = question.votes.filter(form_id=form_id[0]).values('value')[0]['value']
                if vote == '':
                    raise IndexError
                if question.type == "MultiScale":
                    for v in vote.split(', '):
                        row.append(v)
                else:
                    row.append(vote)
            except IndexError:
                print question.type
                if question.type == "MultiScale":
                    for v in question.choices.all():
                        row.append(' ')
                else:
                    row.append(' ')

        table.append(row)

    return {"table": table, "questions": poll.questions.all(), "poll": poll}


def get_results(request, object_id):
    return JsonResponse({"html": render_to_string('website/result_table.html', results(request, object_id))})


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def get_results_excel(request, object_id):
    results_dict = results(request, object_id)
    workbook = xlwt.Workbook()
    fname = slugify(results_dict['poll'].title[:30])
    sheet = workbook.add_sheet(fname)
    cell = 1
    row = 0
    sheet.write(row, 0, 'Data')
    locale.setlocale(locale.LC_ALL, "")
    for question in results_dict['questions']:
        if question.type == u"MultiScale":
            for choice in question.choices.all():
                sheet.write(row, cell, choice.title)
                cell += 1
        else:
            sheet.write(row, cell, question.title)
            cell += 1
    row = 1
    for r in results_dict['table']:
        cell = 0
        for c in r:
            if cell == 0:
                c = datetime_from_utc_to_local(c).strftime(u'%d-%m-%y %H:%M')
            if c.isdigit():
                sheet.write(row, cell, int(c))
            else:
                sheet.write(row, cell, c)
            cell += 1
        row += 1
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % fname
    workbook.save(response)
    return response
