from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import get_object_or_404
from .models import Participant, Organizer
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def participant_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='account_login'):
    def check_participant(user):
        if not user.is_active:
            return False
        participant = Participant.objects.filter(email=user.email).first()
        if participant is None:
            return False
        return True

    def actual_decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not check_participant(request.user):
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return actual_decorator(function)
    return actual_decorator


def organizer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='organizer_login'):
    def check_organizer(user):
        if not user.is_active:
            return False
        organizer = Organizer.objects.filter(email=user.email).first()
        if organizer is None:
            return False
        return True
    def actual_decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not check_organizer(request.user):
                return redirect('home')
            request.organizer = Organizer.objects.filter(email=request.user.email).first()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return actual_decorator(function)
    return actual_decorator