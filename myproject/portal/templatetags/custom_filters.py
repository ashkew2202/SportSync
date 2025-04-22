from django import template

register = template.Library()

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.filter
def male_filter(participants):
    return [participant for participant in participants if participant.gender=='M']

@register.filter
def female_filter(participants):
    return [participant for participant in participants if participant.gender=='F']