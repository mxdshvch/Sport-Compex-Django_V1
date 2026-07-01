from django import template

register = template.Library()

@register.simple_tag
def get_schedule_hours():
    """Возвращает список часов с 7:00 до 22:00"""
    return range(7, 23)

@register.filter
def hours_range(value):
    """Фильтр для создания диапазона часов с 7:00 до 22:00"""
    return range(7, 23) 