from django import template

register = template.Library()
import os

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)



@register.filter
def filename(value):
    return os.path.basename(value)

