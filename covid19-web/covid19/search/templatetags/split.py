"""extra template tags
"""

from django import template

register = template.Library()  # pylint: disable=invalid-name

@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)
