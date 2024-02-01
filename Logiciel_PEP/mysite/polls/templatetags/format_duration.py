from django import template
from django.utils import timesince
register = template.Library()

@register.filter(name='format_duration')
def format_duration(value):
    if value.total_seconds() < 3600:
        # Less than an hour
        minutes = int(value.total_seconds() // 60)
        return f"{minutes} min"
    elif value.total_seconds() < 86400:
        # Less than a day
        hours = int(value.total_seconds() // 3600)
        return f"{hours} h"
    else:
        # Number of days
        days = int(value.total_seconds() // 86400)
        return f"{days} days"