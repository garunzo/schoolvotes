from django import template

register = template.Library()

@register.simple_tag
def get_user_votes(survey, email):
    return survey.get_user_votes(email)
