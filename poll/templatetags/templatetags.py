from collections import Counter

from django import template
from django.template.defaultfilters import slugify
from typing import List

register = template.Library()


@register.filter
def split(string: str, sep: str):
    return string.split(sep)


@register.filter
def index(array: List, index: int):
    try:
        return array[index]
    except IndexError:
        return ''


@register.filter
def mode(array: List[str]):
    if array:
        return Counter(array).most_common(1)[0][0]
    else:
        return 0


@register.filter
def avg(array: List[str]):
    try:
        votes = list(map(int, array))
        return sum(votes) / float(len(votes))
    except (ZeroDivisionError, ValueError):
        return 0.0


@register.filter
def counter(array: List[str]):
    return Counter(array).items()


@register.filter
def median(array: List):
    if array:
        return sorted(array)[len(array) // 2]
    else:
        return 0.0


@register.filter
def total_avg(array: List):
    return avg([avg(l) for l in array])


@register.filter
def slug(title: str):
    return slugify(title)


@register.filter
def counter(array: List):
    return Counter(array).items()


@register.filter
def get(array: List, index: int):
    try:
        return array[index]
    except IndexError:
        return []
