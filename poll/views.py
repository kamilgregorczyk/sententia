import locale
from typing import List, Dict

import xlwt
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from poll.forms import BaseQuestionFormset
from poll.forms import SingleChoiceForm
from poll.models import Poll, Question, Vote

error_messages = {
    "missing_token": u"""Ankieta jest zabezpieczona indywidualnymi linkami, możesz ją wypełnić tylko posiadając
    link z kluczem.""",
    "token_used": u"""Z tego linku już ktoś głosował w ankiecie i nie można użyć go ponownie.""",
    "already_voted": u"""Już oddałeś/aś głos w tej ankiecie, dziękujemy!""",
}


class ViewPermissions(object):
    check_token = True

    def dispatch(self, request: WSGIRequest, *args, **kwargs):
        self.poll = get_object_or_404(
            Poll.objects.select_related('created_by').prefetch_related('questions', 'tokens', 'questions__choices'),
            code=kwargs["poll_code"], status=1)
        self.token = None
        self.voted_polls = request.session.get('voted_polls', [])
        self.error = False
        if self.poll.auth and not kwargs.get("token", None):
            self.error = True
            return HttpResponse(render_to_string("website/error.html", {"msg": error_messages["missing_token"]}))

        if kwargs.get("token", None) and self.poll.auth:
            self.token = get_object_or_404(self.poll.tokens, code=kwargs.get("token", None))
            if self.token.voted and self.check_token:
                self.error = True
                return HttpResponse(render_to_string("website/error.html", {"msg": error_messages["token_used"]}))

        if self.poll.code in self.voted_polls and self.check_token and not self.poll.auth:
            self.error = True
            return HttpResponse(render_to_string("website/error.html", {"msg": error_messages["already_voted"]}))

        return super(ViewPermissions, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.error:
            raise PermissionDenied
        return super(ViewPermissions, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewPermissions, self).get_context_data(**kwargs)
        context["token"] = self.token
        context["poll"] = self.poll
        return context


class PollStartView(ViewPermissions, TemplateView):
    template_name = "website/start.html"


@method_decorator(csrf_exempt, name='dispatch')
class PollVoteView(ViewPermissions, FormView):
    template_name = 'website/poll.html'

    def get_form_class(self):
        questions_count = self.poll.questions.count()
        self.QuestionFormset = forms.formset_factory(
            SingleChoiceForm,
            BaseQuestionFormset,
            extra=questions_count,
            validate_max=True,
            validate_min=True,
            min_num=questions_count,
            max_num=questions_count
        )
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
        next_values = {"poll_code": self.poll.code}
        self.voted_polls.append(self.poll.code)
        self.request.session["voted_polls"] = self.voted_polls

        if self.token:
            next_values.update({"token": self.token})

        self.poll.save_results(context, self.token)

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poll: Poll = None
        self.table: List = None
        self.questions: List[Question] = None

    def setup(self, poll_id: int, user: User):
        self.poll = Poll.objects.prefetch_related('questions', 'questions__choices', 'questions__votes',
                                                  'allowed_users', 'allowed_groups').get(id=poll_id)
        if not (self.poll.created_by == user
                or user.id in self.poll.allowed_users.values_list('id', flat=True)
                or user.id in self.poll.allowed_groups.values_list('user__id', flat=True)
                ):
            raise PermissionDenied()
        self.questions = list(self.poll.questions.all())
        self.table = self.get_results()

    def get_results(self) -> List[List[str]]:
        form_ids = self.poll.votes.values_list('form_id', 'created_at').distinct('form_id')
        form_ids = sorted(form_ids, key=lambda form_id: form_id[1], reverse=True)
        all_votes = self.poll.questions.values('votes__value', 'votes__form_id', 'id')
        cells_count = len(self.questions) + sum(map(lambda question: question.choices.count() - 1,
                                                    filter(lambda question: question.type == "MultiScale",
                                                           self.questions)))
        table = [[' ' for cell in range(cells_count + 1)] for dummy in form_ids]

        votes_dict: Dict[List[Vote]] = {}
        for vote in all_votes:
            key = vote['votes__form_id']
            if key in votes_dict:
                votes_dict[key].append(vote)
            else:
                votes_dict[key] = [vote]

        for form_index, form_id in enumerate(form_ids):
            table[form_index][0] = timezone.localtime(form_id[1])
            votes = votes_dict[form_id[0]]
            question_index = 1
            for question in self.questions:
                try:
                    optional_vote = list(filter(lambda vote_values: vote_values['id'] == question.id, votes))
                    if optional_vote:
                        vote = optional_vote[0]['votes__value']
                        if vote == '':
                            raise IndexError
                        if question.type == "MultiScale":
                            multiscale_choices = vote.split(', ')
                            for choice_index, multiscale_choice in enumerate(multiscale_choices):
                                table[form_index][question_index] = multiscale_choice
                                question_index += 1
                            question_index -= 1
                        else:
                            table[form_index][question_index] = vote
                except IndexError:
                    pass
                question_index += 1
        return table

    def dispatch(self, request, *args, **kwargs):
        self.setup(kwargs['object_id'], request.user)
        return super(BaseResults, self).dispatch(request, *args, **kwargs)


class PollResultsView(BaseResults):
    def get(self, request, *args, **kwargs):
        template = render_to_string('website/result_table.html',
                                    {"poll": self.poll, "questions": self.questions, "table": self.table})
        return JsonResponse({"html": template})


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
                    c = c.strftime(u'%d-%m-%y %H:%M')
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
