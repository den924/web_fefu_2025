from django import template

register = template.Library()

@register.filter
def filter_by_status(enrollments, status):
    """Фильтр записей на курсы по статусу"""
    return enrollments.filter(status=status)
