from django.shortcuts import render, redirect
from . import decorators
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, login
from .forms import RegistrationForm, OrganizerLoginForm, EventForm
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
    events = Event.objects.filter(organizer=organizer)
    context = {
        'events': events,
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
            request.user.email = form.cleaned_data.get('email')
            request.user.save()
            participant=Participant.objects.create(
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                gender=form.cleaned_data.get('gender'),
                dob=form.cleaned_data.get('dob'),
                phone=form.cleaned_data.get('phone'),
                college=form.cleaned_data.get('college')
            )
            participant.save()
            return redirect('participant_dashboard')
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
            print(request.user)
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
        events = Event.objects.all().distinct()
        context = {
            'participant': participant,
            'teams': teams,
            'matches': matches,
            'events': events,
        }
        return render(request, 'portal/participant.html', context)
    else:
        return render(request, 'portal/participant.html', {'error': 'Participant details not found'})

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.min_size = form.cleaned_data.get('min_size')
            print(request.user)
            event.organizer = Organizer.objects.get(name=request.user)
            event.save()
            return redirect('organizer_dashboard')
    else:
        form = EventForm()
    return render(request, 'portal/add_event.html',{'form':form})

def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    matches = Match.objects.filter(event=event)
    colleges = College.objects.filter(participant__team__event=event).distinct()
    context = {
        'event': event,
        'matches': matches,
        'colleges': colleges,
    }
    return render(request, 'portal/eventDetails.html', context)

def college_members(request, college_id):
    college = College.objects.get(id=college_id)
    team = Team.objects.get(college=college, event__organizer=request.user)
    print(team)
    participants = team.participants.all()
    context = {
        'team': team,
        'college': college,
        'participants': participants,
    }
    return render(request, 'portal/collegeMembers.html', context)

def event_view(request):
    teams = Team.objects.filter(participants__email=request.user.email).distinct()
    context = {
        'teams': teams,
    }
    return render(request, 'portal/eventView.html', context)

def register_participant(request, event_id):
    event = Event.objects.get(id=event_id)
    participant = Participant.objects.get(email=request.user.email)
    team = Team.objects.filter(event=event, college=participant.college, max_size=event.max_size).first()
    if not team:
        team = Team.objects.create(
            event=event,
            college=participant.college,
            captain=participant,
            max_size=event.max_size
        )
        team.addParticipant(participant)
        team.save()
    else:
        team.addParticipant(participant)
        team.save()
    return redirect('events')

def ban_participant(request, participant_id, team_id):
    team = Team.objects.get(id=team_id)
    event = team.event
    participant = Participant.objects.get(id=participant_id)
    if request.method == 'POST':
        participant.banPlayer(event)
        return redirect('events')
    return render(request, 'portal/ban_participant.html', {'participant': participant})