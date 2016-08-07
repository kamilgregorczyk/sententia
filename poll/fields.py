# -*- coding: utf-8 -*-
from django.forms import RadioSelect, CheckboxSelectMultiple, MultiValueField, CharField
from django.forms.widgets import RadioFieldRenderer, CheckboxFieldRenderer


class CustomRadioFieldRenderer(RadioFieldRenderer):
    inner_html = u'<li><div class="radio">{choice_value}{sub_widgets}</div></li>'
    outer_html = u'<ul{id_attr}>{content}</ul>'


class CustomInlineRadioFieldRenderer(RadioFieldRenderer):
    inner_html = u'<li><div class="radio">{choice_value}{sub_widgets}</div></li>'
    outer_html = u'<ul{id_attr} class="inline">{content}</ul>'

    def render(self):
        html = super(CustomInlineRadioFieldRenderer, self).render()
        if "choice" in self.attrs:
            html = u"<p>%s:</p>%s" % (self.attrs['choice'][0], html)
        return html


class CustomRadioSelect(RadioSelect):
    renderer = CustomRadioFieldRenderer


class CustomInlineRadioSelect(RadioSelect):
    renderer = CustomInlineRadioFieldRenderer


class CustomCheckboxFieldRenderer(CheckboxFieldRenderer):
    inner_html = u'<li><div class="checkbox">{choice_value}{sub_widgets}</div></li>'


class CustomCheckboxSelectMultiple(CheckboxSelectMultiple):
    renderer = CustomCheckboxFieldRenderer


class ScaleField(MultiValueField):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('choices')
        numbers = [(i, i) for i in xrange(1, 6)]
        super(ScaleField, self).__init__(*args, **kwargs)
        self.fields = [CharField() for question in questions]

    def compress(self, data_list):
        return ', '.join(data_list)
