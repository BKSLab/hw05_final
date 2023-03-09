from typing import Any

from django import template

register = template.Library()


@register.filter
def addclass(field, css) -> Any:
    return field.as_widget(attrs={'class': css})
