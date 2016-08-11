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
from django.views.generic import FormView
from django.views.generic.base import TemplateView, View

from poll.forms import BaseQuestionFormset
from poll.forms import SingleChoiceForm
from poll.helpers import datetime_from_utc_to_local
from poll.models import Poll, Vote

error_messages = {
    "missing_token": u"""Ankieta jest zabezpieczona indywidualnymi linkami, możesz ją wypełnić tylko posiadając link z kluczem.""",
    "token_used": u"""Z tego linku już ktoś głosował w ankiecie i nie można go użyć ponownie.""",
    "already_voted": u"""Już oddałeś/aś głos w tej ankiecie, dziękujemy!""",
}


class ViewPermissions(object):
    check_token = True

    def dispatch(self, request, *args, **kwargs):
        self.poll = get_object_or_404(Poll.objects.select_related('created_by').prefetch_related('questions', 'tokens', 'questions__choices'), code=kwargs["poll_code"], status=1)
        self.token = None
        self.voted_polls = request.session.get('voted_polls', [])
        """Missing token"""
        if self.poll.auth and not kwargs.get("token", None):
            return HttpResponse(render_to_string("website/error.html", {"msg": error_messages["missing_token"]}))
        """Token used"""
        if kwargs.get("token", None) and self.poll.auth:
            self.token = get_object_or_404(self.poll.tokens, code=kwargs.get("token", None))
            if self.token.voted and self.check_token:
                return HttpResponse(render_to_string("website/error.html", {"msg": error_messages["token_used"]}))
        if self.poll.code in self.voted_polls and self.check_token and not self.poll.auth:
            return HttpResponse(render_to_string("website/error.html", {"msg": error_messages["already_voted"]}))
        return super(ViewPermissions, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewPermissions, self).get_context_data(**kwargs)
        context["token"] = self.token
        context["poll"] = self.poll
        return context


class PollStartView(ViewPermissions, TemplateView):
    template_name = "website/start.html"


class PollVoteView(ViewPermissions, FormView):
    template_name = 'website/poll.html'

    def get_form_class(self):
        questions_count = self.poll.questions.count()
        self.QuestionFormset = forms.formset_factory(SingleChoiceForm, BaseQuestionFormset, extra=questions_count, validate_max=True, validate_min=True, min_num=questions_count,
                                                     max_num=questions_count)
        return self.QuestionFormset

    def get_form(self, form_class=None):

        form_class = self.get_form_class()
        form_kwargs = self.get_form_kwargs()
        form_kwargs["form_kwargs"] = {"questions": self.poll.questions.all()}
        return form_class(**form_kwargs)

    def get_context_data(self, **kwargs):
        context = super(PollVoteView, self).get_context_data(**kwargs)
        context["formset"] = self.get_form()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form_id = uuid.uuid4()
        with transaction.atomic():
            for index, field in enumerate(context["formset"].cleaned_data):
                if isinstance(field['choice'], type([])):
                    Vote(value=', '.join(field['choice']), form_id=form_id, question=self.poll.questions.all()[index], poll=self.poll).save()
                else:
                    Vote(value=field['choice'], form_id=form_id, question=self.poll.questions.all()[index], poll=self.poll).save()

            next_values = {"poll_code": self.poll.code}
            self.voted_polls.append(self.poll.code)
            self.request.session["voted_polls"] = self.voted_polls
            if self.token:
                next_values.update({"token": self.token})
                self.token.voted = True
                self.token.save(update_fields=["voted"])

        return HttpResponseRedirect(reverse("poll_end", kwargs=next_values))


class PollEndView(ViewPermissions, TemplateView):
    template_name = "website/end.html"
    check_token = False


class PollErrorView(TemplateView):
    template_name = "website/error.html"


class FAQView(TemplateView):
    template_name = 'website/faq.html'


class IndexView(TemplateView):
    template_name = 'website/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["polls"] = Poll.objects.filter(status=1, auth=0, list_status=1)
        return context


class BaseResults(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        self.table = []
        self.poll = Poll.objects.prefetch_related('questions', 'questions__choices', 'questions__votes', 'allowed_users', 'allowed_groups').get(id=kwargs["object_id"])
        self.questions = self.poll.questions.all()
        if not (self.poll.created_by == request.user or request.user in self.poll.allowed_users.all() or request.user.id in self.poll.allowed_groups.values_list('user__id',
                                                                                                                                                                 flat=True)):
            raise PermissionDenied()
        form_ids = list(self.poll.votes.values_list('form_id', 'created_at').distinct('form_id'))
        form_ids.sort(key=lambda k: k[1], reverse=True)
        for form_id in form_ids:
            row = [timezone.localtime(form_id[1])]
            for question in self.poll.questions.all():
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

            self.table.append(row)
        return super(BaseResults, self).dispatch(request, *args, **kwargs)


class PollResultsView(BaseResults):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"html": render_to_string('website/result_table.html', {"poll": self.poll, "questions": self.questions, "table": self.table})})


class ExcelResultsView(BaseResults):
    def get(self, request, *args, **kwargs):
        workbook = xlwt.Workbook()
        fname = slugify(self.poll.title[:30])
        sheet = workbook.add_sheet(fname)
        cell = 1
        row = 0
        sheet.write(row, 0, 'Data')
        locale.setlocale(locale.LC_ALL, "")
        for question in self.questions:
            if question.type == u"MultiScale":
                for choice in question.choices.all():
                    sheet.write(row, cell, choice.title)
                    cell += 1
            else:
                sheet.write(row, cell, question.title)
                cell += 1
        row = 1
        for r in self.table:
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
