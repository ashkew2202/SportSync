from django.shortcuts import render
from . import decorators
from allauth.account.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.backends import ModelBackend
from .forms import RegistrationForm, OrganizerLoginForm
from .models import Participant, Organizer

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

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = request.user
            participant=Participant.objects.create(
                name=form.cleaned_data.get('name'),
                email=user.email,
                gender=form.cleaned_data.get('gender'),
                dob=form.cleaned_data.get('dob'),
                phone=form.cleaned_data.get('phone'),
                college=form.cleaned_data.get('college')
            )
            participant.save()
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'portal/registration.html', {'form': form})

def ologin(request):
    if request.method == 'POST':
        form = OrganizerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                organizer = Organizer.objects.get(name=username)
                if organizer.password == password:  # Verify the password
                    # Start a session manually
                    request.session['organizer_id'] = organizer.id
                    request.session['organizer_name'] = organizer.name
                    return redirect('home')
                else:
                    return render(request, 'portal/ologin.html', {'error': 'Invalid username or password'})
            except Organizer.DoesNotExist:
                return render(request, 'portal/ologin.html', {'error': 'Organizer does not exist'})
    else:
        form = OrganizerLoginForm()
    return render(request, 'portal/ologin.html', {'form': form})

def prelogin(request):
    return render(request, 'portal/prelogin.html')

def profile(request):
    if request.user.is_authenticated:
        try:
            participant = Participant.objects.filter(email=request.user.email)
            return render(request, 'account/profile.html', {'participant': participant[0]})
        except Participant.DoesNotExist:
            return render(request, 'account/profile.html', {'error': 'Participant details not found'})
    else:
        return redirect('login')