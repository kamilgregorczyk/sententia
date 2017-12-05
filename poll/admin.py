import datetime

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe
from nested_admin.nested import NestedStackedInline, NestedModelAdmin
from tabbed_admin import TabbedModelAdmin

from poll.forms import PollAdminForm, TokenInlineForm
from poll.models import Poll, Question, Choice, Token, get_code


class ChoiceInline(NestedStackedInline):
    is_sortable = False
    model = Choice
    extra = 0
    fields = ['title']


class TokenInline(admin.TabularInline):
    model = Token
    form = TokenInlineForm
    extra = 0
    inlines = []
    readonly_fields = ['voted', 'link']
    sortable_field_name = "order"

    def link(self, obj):
        link = reverse('poll', kwargs={"poll_code": obj.poll.code, "token": obj.code})
        return mark_safe('<a href="{0}{1}" target="_blank">{0}{1}</a>'.format(settings.BASE_URL, link))

    link.short_description = u"Link"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(TokenInline, self).get_formset(request, obj, **kwargs)
        formset.form.saveasnew = request.POST.get('_saveasnew', False)
        return formset


class QuestionInline(NestedStackedInline):
    model = Question
    extra = 0
    min_num = 1
    inlines = [ChoiceInline]
    fields = (('title', 'type', 'required',), 'order',)
    sortable_field_name = "order"


class PollAdmin(TabbedModelAdmin, NestedModelAdmin):
    save_as = True
    inlines = [QuestionInline, TokenInline]
    form = PollAdminForm
    list_display = ['title', 'get_results_count', 'absolute_link', '_status', '_list_status', '_auth', 'created_by']
    search_fields = ['title', 'absolute_link', 'created_by', 'description']
    tab_main = (
        (None, {
            'fields': ('title', 'code', 'status', 'list_status', 'auth', 'created_by', 'description')
        }),
    )
    readonly_fields = ['created_by']

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

    absolute_link.short_description = u'Link'
    absolute_link.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        form = super(PollAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.saveasnew = request.POST.get('_saveasnew', False)
        return form

    def get_tabs(self, request, obj=None):
        if obj and request.user != obj.created_by:
            return [
                (u'Podstawowe dane', self.tab_main),
                (u'Pytania', self.tab_questions),
                (u'Tokeny', self.tab_tokens)
            ]
        return [
            (u'Podstawowe dane', self.tab_main),
            (u'Pytania', self.tab_questions),
            (u'Tokeny', self.tab_tokens),
            (u'Uprawnienia', self.tab_permissions)
        ]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        poll = Poll.objects.prefetch_related('questions', 'questions__choices', 'questions__votes', 'allowed_users',
                                             'allowed_groups').get(id=object_id)
        if not (poll.created_by == request.user
                or request.user in poll.allowed_users.all()
                or request.user.id in poll.allowed_groups.values_list('user__id', flat=True)
                ):
            raise PermissionDenied()
        change_view = super(PollAdmin, self).change_view(request, object_id, form_url, extra_context)
        return change_view

    def get_queryset(self, request):
        return super(PollAdmin, self).get_queryset(request).filter(
            Q(created_by=request.user) | Q(allowed_users=request.user) | Q(
                allowed_groups__user=request.user)).distinct()

    def save_related(self, request, form, formsets, change):
        if "_saveasnew" in request.POST:
            formsets.remove(list(filter(lambda x: x.__class__.__name__ == "TokenFormFormSet", formsets))[0])
        return super(PollAdmin, self).save_related(request, form, formsets, change)

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.updated_at = datetime.datetime.now()

        if "_saveasnew" in request.POST:
            obj.code = get_code(Poll)
            obj.votes.all().delete()
            obj.tokens.all().delete()

        return super(PollAdmin, self).save_model(request, obj, form, change)

    class Media:
        css = {'all': ['poll/css/admin.css', 'poll/css/select2.min.css', 'website/css/font-awesome.min.css',
                       'poll/css/grid12.css']}
        js = ['admin/js/jquery.js', 'poll/js/admin.js', 'poll/js/select2.full.min.js', 'website/js/clipboard.min.js',
              'poll/js/loader.js']


admin.site.register(Poll, PollAdmin)
