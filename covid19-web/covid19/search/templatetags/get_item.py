"""extra template tags
"""

from django.template.defaulttags import register
from django import template

register = template.Library()  # pylint: disable=invalid-name

@register.filter
def get_item(dictionary, key):

	try:
		result = dictionary.get(key)
	except:
		result = ''

	return result