from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME

def candidate_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='account_login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_candidate,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def organizer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='account_login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_organizer,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator