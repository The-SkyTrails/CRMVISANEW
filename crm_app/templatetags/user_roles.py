# templatetags/user_roles.py
from django import template

register = template.Library()

@register.filter
def is_admin(user):
    return user.user_type == "2"

@register.filter
def is_employee(user):
    return user.user_type == "3"



@register.filter
def has_access(user, allowed_roles):
    """Generic filter to check if a user has access based on allowed roles."""
    allowed_roles_list = allowed_roles.split(",")  # Pass roles as a comma-separated string
    return user.user_type in allowed_roles_list
