from collections import Counter

from django import template
from django.template.defaultfilters import slugify

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


@register.filter
def mode(array):
    return Counter(array).most_common(1)[0][0]


@register.filter
def avg(array):
    return sum(array) / float(len(array))


@register.filter
def median(array):
    return sorted(array)[len(array) // 2]


@register.filter
def total_avg(array):
    return avg([avg(l) for l in array])


@register.filter
def slug(title):
    return slugify(title)


@register.filter
def get(array, index):
    try:
        return array[index]
    except IndexError:
        return []
