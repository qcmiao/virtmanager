from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def counter(value, page):
    pagesize = 10
    return (page - 1) * pagesize + value
