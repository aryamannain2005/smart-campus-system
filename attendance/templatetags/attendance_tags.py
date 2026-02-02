"""
Custom template tags for Attendance Management System.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        if total == 0:
            return 0
        return round((value / total) * 100, 1)
    except (ValueError, TypeError):
        return 0


@register.filter
def status_badge_class(status):
    """Return Bootstrap badge class for attendance status."""
    classes = {
        'present': 'bg-success',
        'absent': 'bg-danger',
        'late': 'bg-warning text-dark',
        'excused': 'bg-secondary',
    }
    return classes.get(status, 'bg-secondary')


@register.filter
def priority_badge_class(priority):
    """Return Bootstrap badge class for notification priority."""
    classes = {
        'low': 'bg-info',
        'medium': 'bg-primary',
        'high': 'bg-warning text-dark',
        'urgent': 'bg-danger',
    }
    return classes.get(priority, 'bg-secondary')
