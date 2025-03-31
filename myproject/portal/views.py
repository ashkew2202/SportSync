from django.shortcuts import render, redirect
from . import decorators
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, login
from .forms import RegistrationForm, OrganizerLoginForm
from .models import Participant, Organizer, Match, Event, Team, BannedParticipants, College
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import MatchForm

# Create your views here.
def base(request):
    return render(request,'base.html')

def home(request):
    return render(request,'portal/home.html')

@decorators.candidate_required
def candidate_entry(request):
    return render(request, 'portal/candidate.html')

@login_required(login_url='organizer_login')
def organizer_entry(request):
    organizer = request.user
    matches = Match.objects.filter(organizer=organizer)
    context = {
        'matches': matches,
    } 
    return render(request, 'portal/organizer.html', context)

def login(request):
    return render(request, 'portal/prelogin.html')

@login_required(login_url='account_login')
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
                    # Specify the backend explicitly
                    organizer.backend = 'django.contrib.auth.backends.OrganizerBackend'
                    auth_login(request, organizer, backend='portal.backends.OrganizerBackend')
                    return redirect('organizer_dashboard')
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
            return render(request, 'account/profile.html', {'participant': participant[0],'user':request.user})
        except Participant.DoesNotExist:
            return render(request, 'account/profile.html', {'error': 'Participant details not found'})
    else:
        return redirect('account_login')

def match_details(request, match_id):
    match = Match.objects.get(id=match_id)
    teams = Team.objects.filter(match=match)
    context = {
        'match': match,
        'teams': teams,
    }
    return render(request, 'portal/matchDetails.html', context)

def update_match(request, match_id):
    match = Match.objects.get(id=match_id)
    if request.method == 'POST':
        match.date = request.POST.get('date')
        match.venue = request.POST.get('location')
        match.save()
        return redirect('match_details', match_id=match.id)
    return render(request, 'portal/updateMatch.html', {'match': match})

def delete_match(request, match_id):
    match = Match.objects.get(id=match_id)
    if request.method == 'POST':
        match.delete()
        return redirect('organizer_dashboard')
    return render(request, 'portal/deleteMatch.html', {'match': match})

def addMatch(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.organizer = request.user
            match.save()
            return redirect('organizer_dashboard')
    else:
        form = MatchForm()

    return render(request, 'portal/addMatch.html', {'form': form})

@login_required(login_url='account_login')
def participant_entry(request):
    user = request.user
    try:
        participant = Participant.objects.get(email=user.email)
    except Participant.DoesNotExist:
        participant = None
    if participant:
        teams = Team.objects.filter(participants=participant).distinct()
        matches = Match.objects.filter(teams__in=teams).distinct()
        context = {
            'participant': participant,
            'teams': teams,
            'matches': matches,
        }
        return render(request, 'portal/participant.html', context)
    else:
        return render(request, 'portal/participant.html', {'error': 'Participant details not found'})