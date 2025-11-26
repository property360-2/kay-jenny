from django import template

register = template.Library()


@register.filter
def index(list_obj, i):
    """Access list item by index"""
    try:
        return list_obj[int(i)]
    except (IndexError, ValueError, TypeError):
        return None


@register.filter
def get_item(dictionary, key):
    """Access dictionary item by key"""
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None
