'''
Created on 21.03.2013

@author: hauck
'''
from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='contains')
def contains(value, arg):
    return arg in value

@register.filter(name='klass')
def klass(ob):
    return ob.__class__.__name__

@register.filter(name='to_int')
def to_int(ob):
    if ob:
        return int(ob)
    else:
        return

@register.filter(name='to_string')
def to_string(ob):
    if ob:
        return str(ob)
    else:
        return
    
@register.filter(name="to_class_name")
def to_class_name(value):
    return value.__class__.__name__

@register.filter(name="string_to_list")
def string_to_list(id_string, delimiter):
    return id_string.split(delimiter)

@register.filter(name="get_value_from_dict")
def get_value_from_dict(dict, key):
    return dict[str(key)]

@register.filter(name="value_from_settings")
def value_from_settings(name):
    return getattr(settings, name, "")

