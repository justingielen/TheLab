from django import template
import datetime

register = template.Library()

@register.filter
def format_duration(value):
    if isinstance(value, datetime.timedelta):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        duration_str = ""
        if hours > 0:
            duration_str += f"{hours} hour{'s' if hours > 1 else ''}"
        if minutes > 0:
            if hours > 0:
                duration_str += " "
            duration_str += f"{minutes} minute{'s' if minutes > 1 else ''}"

        return duration_str

    return value