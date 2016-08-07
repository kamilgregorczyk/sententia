import datetime
import json

from django.conf import settings
from django.contrib import admin
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
    list_display = ['title', 'status']
    inlines = [QuestionInline, TokenInline]
    form = PollAdminForm
    tab_main = (
        (None, {
            'fields': ('title', 'code', 'status', 'list_status', 'auth', 'description')
        }),
    )
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
        tabs = self.tabs
        if obj and request.user != obj.created_by:
            tabs = [
                (u'Podstawowe dane', self.tab_main),
                (u'Pytania', self.tab_questions),
                (u'Tokeny', self.tab_tokens)
            ]

        self.tabs = tabs
        return super(PollAdmin, self).get_tabs(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        poll = Poll.objects.get(id=object_id)
        max_votes = range(max([question.votes.count() for question in poll.questions.all()]))
        extra_context = {
            "max_votes": max_votes,
            "table": json.loads(get_results(request, object_id).content),
        }
        return super(PollAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_queryset(self, request):
        return super(PollAdmin, self).get_queryset(request).filter(Q(created_by=request.user) | Q(allowed_users=request.user) | Q(allowed_groups__user=request.user)).distinct()

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.updated_at = datetime.datetime.now()
        return super(PollAdmin, self).save_model(request, obj, form, change)

    class Media:
        css = {'all': ['poll/css/admin.css', 'poll/css/select2.min.css']}
        js = ['admin/js/jquery.js', 'poll/js/admin.js', 'poll/js/select2.full.min.js',
              'https://use.fontawesome.com/4c8a121ad3.js']


admin.site.register(Poll, PollAdmin)
