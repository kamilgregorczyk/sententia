# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.utils import ErrorDict
from django.forms.widgets import Textarea

from poll.fields import CustomRadioSelect, CustomCheckboxSelectMultiple, CustomInlineRadioSelect, ScaleField
from poll.models import Poll, gen_code, get_code, Token
from poll.widgets import ScaleWidget


class PollAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PollAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['allowed_groups'].queryset = Group.objects.filter(permissions=None)
            change_perm = Permission.objects.get(name='Can change Ankieta')
            self.fields['allowed_users'].queryset = User.objects.filter(
                Q(groups__permissions=change_perm) | Q(user_permissions=change_perm)).distinct().exclude(
                pk=self.current_user.id)
        except KeyError:
            pass
        if self.instance.pk:
            self.fields['code'].widget.attrs['readonly'] = True
            self.fields['code'].help_text = u'Adres ankiety: <a href="{0}{1}" target="_blank">{0}{1}</a>'.format(
                settings.BASE_URL,
                reverse('poll', kwargs={"poll_code": self.instance.code}))
        else:
            code = get_code(Poll)
            self.fields['code'].initial = code
            self.fields['code'].widget.attrs['readonly'] = True
            self.fields['code'].help_text = u'Adres ankiety: %s%s' % (
            settings.BASE_URL, reverse('poll', kwargs={"poll_code": code}))

    def add_error(self, field, error):
        if self.saveasnew and field is None and "code" not in error.error_dict:
            return super(PollAdminForm, self).add_error(field, error)

    class Meta:
        model = Poll
        fields = '__all__'


class TokenInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TokenInlineForm, self).__init__(*args, **kwargs)

    def add_error(self, field, error):
        if self.saveasnew and field is None and "code" not in error.error_dict:
            return super(TokenInlineForm, self).add_error(field, error)

    class Meta:
        model = Token
        fields = "__all__"


class QuestionFormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        super(QuestionFormBase, self).__init__(*args, **kwargs)

    def as_p(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row=u'<p%(html_class_attr)s>%(label)s <span class="help-text">%(help_text)s</span> %(field)s</p>',
            error_row=u'%s',
            row_ender=u'</p>',
            help_text_html=u' <span class="helptext">%s</span>',
            errors_on_separate_row=True)


class SingleChoiceForm(QuestionFormBase):
    def __init__(self, *args, **kwargs):
        super(SingleChoiceForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.ChoiceField(
            choices=[(choice, choice) for choice in self.question.choices.values_list('title', flat=True)],
            widget=CustomRadioSelect,
            required=self.question.required,
            label=self.question.title)


class MultiChoiceForm(QuestionFormBase):
    def __init__(self, *args, **kwargs):
        super(MultiChoiceForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.MultipleChoiceField(
            choices=[(choice, choice) for choice in self.question.choices.values_list('title', flat=True)],
            widget=CustomCheckboxSelectMultiple,
            required=self.question.required,
            label=self.question.title)


class MultiScaleForm(QuestionFormBase):
    def __init__(self, *args, **kwargs):
        super(MultiScaleForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = ScaleField(require_all_fields=self.question.required,
                                           label=self.question.title,
                                           widget=ScaleWidget(attrs={
                                               "choices": self.question.choices.values_list('title', flat=True)}),
                                           choices=self.question.choices.values_list('title', flat=True),
                                           help_text=u"5 oznacza najlepszą ocenę")


class ScaleForm(QuestionFormBase):
    def __init__(self, *args, **kwargs):
        super(ScaleForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.ChoiceField(choices=[(i, i) for i in xrange(1, 6)],
                                                  widget=CustomInlineRadioSelect,
                                                  required=self.question.required,
                                                  label=self.question.title,
                                                  help_text=u"5 oznacza najlepszą ocenę")


class TextAreaForm(QuestionFormBase):
    def __init__(self, *args, **kwargs):
        super(TextAreaForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.CharField(required=self.question.required, label=self.question.title,
                                                widget=Textarea)
        self.fields['choice'].widget.attrs["class"] = "form-control"
        self.fields['choice'].widget.attrs["rows"] = "5"


class BaseQuestionFormset(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.questions = kwargs['form_kwargs'].pop('questions')
        super(BaseQuestionFormset, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        self.form = globals()["%sForm" % self.questions[i].type]
        return super(BaseQuestionFormset, self)._construct_form(i, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super(BaseQuestionFormset, self).get_form_kwargs(index)
        kwargs['question'] = self.questions[index]
        return kwargs
