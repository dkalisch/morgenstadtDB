'''
Created on 21.03.2013

@author: hauck
'''
from django import template

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
    
@register.filter(name="to_class_name")
def to_class_name(value):
    return value.__class__.__name__

