from django import template

register = template.Library()
import os

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)



@register.filter
def filename(value):
    return os.path.basename(value)




@register.simple_tag
def cycle_class(counter, *classes):
    return classes[(counter - 1) % len(classes)]