from django import template
import re

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """
    Разделяет строку по указанному разделителю.
    Использование: {{ "a,b,c"|split:"," }}
    """
    return value.split(delimiter)

@register.filter
def get_item(dictionary, key):
    """
    Фильтр для получения элемента из словаря по ключу
    Использование: {{ my_dict|get_item:key_var }}
    """
    return dictionary.get(key) 