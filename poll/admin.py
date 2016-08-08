# coding=utf-8
import datetime
import json
from random import randint

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe
from nested_admin import NestedModelAdmin, NestedStackedInline
from tabbed_admin import TabbedModelAdmin

from poll.forms import PollAdminForm
from poll.models import Poll, Question, Choice, Token
from poll.views import get_results


class ChoiceInline(NestedStackedInline):
    model = Choice
    extra = 0
    fields = ['title', 'order']
    sortable_field_name = "order"


class TokenInline(admin.TabularInline):
    model = Token
    extra = 0
    inlines = []
    readonly_fields = ['voted', 'link']
    sortable_field_name = "order"

    def link(self, obj):
        return mark_safe('<a href="{0}{1}" target="_blank">{0}{1}</a>'.format(settings.BASE_URL, reverse('poll', kwargs={"poll_code": obj.poll.code, "token": obj.code})))

    link.short_description = u"Link"


class QuestionInline(NestedStackedInline):
    model = Question
    extra = 0
    min_num = 1
    inlines = [ChoiceInline]
    fields = (('title', 'type', 'required',), 'order',)
    sortable_field_name = "order"


class PollAdmin(TabbedModelAdmin, NestedModelAdmin):
    inlines = [QuestionInline, TokenInline]
    form = PollAdminForm
    list_display = ['title', 'absolute_link', '_status', '_list_status', '_auth', 'created_by']
    search_fields = ['title', 'absolute_link', 'created_by', 'description']
    tab_main = (
        (None, {
            'fields': ('title', 'code', 'status', 'list_status', 'auth', 'created_by', 'description')
        }),
    )
    readonly_fields = ['created_by']

    def _status(self, obj):
        return bool(obj.status)

    _status.short_description = u'Status'
    _status.boolean = True

    def _list_status(self, obj):
        return bool(obj.list_status)

    _list_status.short_description = u'Publikowana na głównej'
    _list_status.boolean = True

    def _auth(self, obj):
        return bool(obj.auth)

    _auth.short_description = u'Autoryzowana tokenami'
    _auth.boolean = True

    def absolute_link(self, obj):
        return '<a href="{0}" target="_blank">{0}</a>'.format(obj.get_absolute_url())

    absolute_link.short_description = u'Autoryzowana tokenami'
    absolute_link.allow_tags = True

    tab_permissions = (
        (None, {
            'fields': ('allowed_users', 'allowed_groups',)
        }),
    )
    tab_questions = (
        QuestionInline,
    )
    tab_tokens = (
        TokenInline,
    )
    tabs = [
        (u'Podstawowe dane', tab_main),
        (u'Pytania', tab_questions),
        (u'Tokeny', tab_tokens),
        (u'Uprawnienia', tab_permissions)
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(PollAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_tabs(self, request, obj=None):
        if obj and request.user != obj.created_by:
            self.tabs = [
                (u'Podstawowe dane', self.tab_main),
                (u'Pytania', self.tab_questions),
                (u'Tokeny', self.tab_tokens)
            ]

        return self.tabs

    def change_view(self, request, object_id, form_url='', extra_context=None):
        poll = Poll.objects.prefetch_related('questions', 'questions__choices', 'questions__votes', 'allowed_users', 'allowed_groups').get(id=object_id)
        if not (poll.created_by == request.user or request.user in poll.allowed_users.all() or request.user.id in poll.allowed_groups.values_list('user__id', flat=True)):
            raise PermissionDenied()
        max_votes = range(max([question.votes.count() for question in poll.questions.all()]))
        extra_context = {
            "max_votes": max_votes,
            "table": json.loads(get_results(request, object_id).content),
        }
        change_view = super(PollAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)
        return change_view

    def get_queryset(self, request):
        return super(PollAdmin, self).get_queryset(request).filter(Q(created_by=request.user) | Q(allowed_users=request.user) | Q(allowed_groups__user=request.user)).distinct()

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.updated_at = datetime.datetime.now()
        return super(PollAdmin, self).save_model(request, obj, form, change)

    class Media:
        css = {'all': ['poll/css/admin.css', 'poll/css/select2.min.css', 'website/css/font-awesome.min.css']}
        js = ['admin/js/jquery.js', 'poll/js/admin.js', 'poll/js/select2.full.min.js', 'website/js/clipboard.min.js']


admin.site.register(Poll, PollAdmin)
