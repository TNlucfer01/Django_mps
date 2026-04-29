from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Return dictionary[key], used in templates as {{ dict|get_item:key }}."""
    return dictionary.get(key)
