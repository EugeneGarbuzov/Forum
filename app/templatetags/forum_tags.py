from django import template

register = template.Library()


@register.simple_tag
def tags(tag_names):
    return 'Tags: ' + ', '.join(tag_names)
