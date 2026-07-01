from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Фильтр для получения элемента из словаря по ключу
    """
    return dictionary.get(key) 