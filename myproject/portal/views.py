from django.shortcuts import render
from . import decorators
from allauth.account.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login

# Create your views here.
def base(request):
    return render(request,'base.html')

def home(request):
    return render(request,'portal/home.html')

@decorators.candidate_required
def candidate_entry(request):
    return render(request, 'portal/candidate.html')

@decorators.organizer_required
def organizer_entry(request):
    return render(request, 'portal/organizer.html')

def login(request):
    return render(request, 'portal/prelogin.html')

