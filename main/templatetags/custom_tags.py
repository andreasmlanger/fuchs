from django import template
import random

register = template.Library()


@register.filter
def shuffle(arr):
    tmp = arr.copy()
    random.shuffle(tmp)
    return tmp


@register.filter
def hashed(h, key):
    return h[key]


@register.filter
def replace_whitespace_dash(x):
    return x.replace(' ', '-')
