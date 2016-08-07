from django import template

register = template.Library()


@register.filter
def split(string, sep):
    return string.split(sep)


@register.filter
def index(array, index):
    try:
        return array[index]
    except IndexError:
        return ''
