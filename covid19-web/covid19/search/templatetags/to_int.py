"""extra template tags
"""

from django.template.defaulttags import register
from django import template

register = template.Library()  # pylint: disable=invalid-name

@register.filter
def to_int(string):
    return int(string)
