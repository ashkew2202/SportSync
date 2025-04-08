from django.shortcuts import render, redirect
from . import decorators
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, login
from .forms import RegistrationForm, OrganizerLoginForm, EventForm
from .models import Participant, Organizer, Match, Event, Team, BannedParticipants, College
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import MatchForm, TeamForm
import django_tables2 as tables
from django.core.mail import send_mail
from django.conf import settings

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
    print(match.teams)
    teams = match.teams.all()
    print(match)
    form = TeamForm()
    context = {
        'match': match,
        'teams': teams,
        'form': form
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
            time = form.cleaned_data['time']
            date = form.cleaned_data['date']
            venue = form.cleaned_data['venue']
            event = form.cleaned_data['event']
            teams = form.cleaned_data['teams']
            teams = [team for team in teams if team.event.id == event.id]
            if event.gender in ['Men', 'Women']:
                team_gender = 'M' if event.gender == 'Men' else 'F'
                print(team_gender)
                for team in teams:
                    if any(participant.gender != team_gender for participant in team.participants.all()):
                        print(any(participant.gender) for participant in team.participants.all())
                        return render(request, 'portal/addMatch.html', {
                            'form': form,
                            'error': f'Team members must all be {team_gender.lower()} to participate in this event.'
                        })
            organizer = request.user
            match = Match.objects.create(
                time=time,
                date=date,
                venue=venue,
                event=event,
                organizer=organizer,
            )
            match.teams.set(teams)
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
        events = Event.objects.filter(team_event__participants=participant).distinct()
        print(events)
        print(teams)
        
        print(matches)
        matches = list(set(matches))  # Remove duplicates
        
        events = Event.objects.filter(
            gender__in=['Mixed', 'Men' if participant.gender == 'M' else 'Women']
        ).distinct()
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
    participants = Participant.objects.filter(team__event=event)  # Default value for participants

    if request.method == 'GET':
        filter_by = request.GET.get('filter_by')
        filter_value = request.GET.get('filter_value')
        if filter_by == 'name':
            participants = Participant.objects.filter(name=filter_value, team__event=event)
        elif filter_by == 'email':
            participants = Participant.objects.filter(email=filter_value, team__event=event)
        elif filter_by == 'phone':
            participants = Participant.objects.filter(phone=filter_value, team__event=event)
        elif filter_by == 'college':
            participants = Participant.objects.filter(college=filter_value, team__event=event)
        elif filter_by == 'gender':
            participants = Participant.objects.filter(gender=filter_value, team__event=event)
        else:
            participants = Participant.objects.filter(team__event=event)
        
        college_filter_by = request.GET.get('college_filter_by')
        college_filter_value = request.GET.get('college_filter_value')
        if college_filter_by == 'name':
            colleges = College.objects.filter(name=college_filter_value, participant__team__event=event)
        elif college_filter_by == 'address':
            colleges = College.objects.filter(address=college_filter_value, participant__team__event=event)
        elif college_filter_by == 'pincode':
            colleges = College.objects.filter(pincode=college_filter_value, participant__team__event=event)
        else:
            colleges = College.objects.filter(participant__team__event=event)
    context = {
        'event': event,
        'matches': matches,
        'colleges': colleges,
        'participants': participants,
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
    # Ensure the team captain's gender matches the event requirement
    if event.gender and event.gender != 'Mixed':
        if (event.gender == 'Men' and participant.gender != 'Male') or (event.gender == 'Women' and participant.gender != 'Female'):
            return render(request, 'portal/register_participant.html', {
                'error': f'The team captain must be {event.gender.lower()} for this event.'
            })
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
        # Confirm the gender of the team members matches the event requirement
        if event.gender and event.gender != 'Mixed' and participant.gender != event.gender:
            if (event.gender == 'Men' and participant.gender != 'Male') or (event.gender == 'Women' and participant.gender != 'Female'):
                return render(request, 'portal/register_participant.html', {
                    'error': f'This event is restricted to {event.gender.lower()} participants only.'
                })
        # Send an email to the captain of the team
        if team.captain:
            subject = "New Participant Request for Your Team"
            message = f"""
            Dear {team.captain.name},

            A new participant has requested to join your team for the event "{event}".
            Here are the details of the participant:

            Name: {participant.name}
            Email: {participant.email}
            Phone: {participant.phone}
            Gender: {participant.gender}
            College: {participant.college.name}

            Please review the request and take appropriate action.

            Best regards,
            SportSync Team
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [team.captain.email]

            send_mail(subject, message, from_email, recipient_list)
    return redirect('events')

def ban_participant(request, participant_id, team_id):
    team = Team.objects.get(id=team_id)
    event = team.event
    participant = Participant.objects.get(id=participant_id)
    if request.method == 'POST':
        participant.banPlayer(event)
        return redirect('events')
    return render(request, 'portal/ban_participant.html', {'participant': participant})

def addTeam(request, match_id):
    if request.method == 'POST':
        match = Match.objects.get(id=match_id)
        event = match.event
        form = TeamForm(request.POST)
        event_form = form.cleaned_data['event']
        print(event_form)
        if event_form != event:
            return redirect(request.path_info)
        team = form.cleaned_data['team']
        if team.max_size < event.min_size:
            return redirect(request.path_info)
        match.addTeam(team)
        match.save()
        return redirect('match_details', match_id=match.id)
    else:
        form = TeamForm()

    return render(request, 'portal/addTeam.html', {'form': form})

def team_details(request, team_id):
    team = Team.objects.get(id=team_id)
    participants = team.participants.all()
    participants_ofSameCollege = Participant.objects.filter(college=team.college).exclude(id__in=participants.values_list('id', flat=True))
    if 1+participants.count() < team.max_size:
        is_team_full = False
    else:
        is_team_full = True
    context = {
        'participants_ofSameCollege': participants_ofSameCollege,
        'is_team_full': is_team_full,
        'team': team,
        'participants': participants,
    }
    return render(request, 'portal/teamDetails.html', context)

def addTeamMembers(request, team_id):
    team = Team.objects.get(id=team_id)
    participants_ofSameCollege = Participant.objects.filter(college=team.college).exclude(id__in=team.participants.values_list('id', flat=True))

    if request.method == 'POST':
        participant_id = request.POST.get('new_member')
        if participant_id:
            participant = Participant.objects.get(id=participant_id)
            if team.participants.count() < team.max_size:
                team.participants.add(participant)
                team.save()
                return redirect('team_details', team_id=team.id)
            else:
                return render(request, 'portal/addTeamMembers.html', {
                    'team': team,
                    'participants_ofSameCollege': participants_ofSameCollege,
                    'error': 'Team is already full.'
                })

    return render(request, 'portal/addTeamMembers.html', {
        'team': team,
        'participants_ofSameCollege': participants_ofSameCollege
    })
    
def update_status(request, match_id):
    match = Match.objects.get(id=match_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        match.status = status
        match.save()
        return redirect('match_details', match_id=match.id)
    return render(request, 'portal/update_status.html', {'match': match})