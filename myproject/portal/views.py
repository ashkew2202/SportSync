from django.shortcuts import render, redirect
from .decorators import participant_required, organizer_required
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, login
from .forms import RegistrationForm, OrganizerLoginForm, EventForm
from .models import Participant, Organizer, Match, Event, Team, BannedParticipants, College, CricketScore, SingleScoringForSwimming, FootballScore, BadmintonScore, FeedBack, SingleScoringForAthletics
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import MatchForm, TeamForm, CricketScoring, FootballScoring, BadmintonScoring, AthleticsScoreForm, AthleticsScoreFormSet, SingleScoringForAthleticsForm
import django_tables2 as tables
from django.core.mail import send_mail
from django.conf import settings
from allauth.socialaccount.models import SocialAccount
from django.utils.crypto import get_random_string
# Create your views here.
def base(request):
    return render(request,'base.html')

def home(request):
    return render(request,'portal/home.html')

def candidate_entry(request):
    return render(request, 'portal/candidate.html')

@organizer_required
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
            verification_token = get_random_string(8, allowed_chars='0123456789')
            request.session['verification_token'] = verification_token
            request.session['is_email_verified'] = False
            subject = "Verify Your Email Address"
            message = f"""
            Dear {request.user.username},

            Your OTP for email verification is: {verification_token}

            If you did not request this, please ignore this email.

            Best regards,
            SportSync Team
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [form.cleaned_data.get('email')]
            send_mail(subject, message, from_email, recipient_list)
            request.session['registration_form_data'] = request.POST
            return redirect('verify_participant')
            
    else:
        form = RegistrationForm()

    return render(request, 'portal/registration.html', {'form': form})
@login_required(login_url='account_login')
def verify_email_prompt(request):
    if request.method == 'POST':
        verification_token = request.POST.get('verification_token')
        try:
            if verification_token == request.session.get('verification_token'):
                request.session['is_email_verified'] = True
                user = request.user
                
            else:
                return render(request, 'portal/verify_email_prompt.html', {'error': 'Invalid verification token'})
            if request.session.get('is_email_verified'):
                form = RegistrationForm(request.session.get('registration_form_data'))
                if form.is_valid():
                    user.email = form.cleaned_data.get('email')
                    user.save()
                    print(user.email)
                    print(form.cleaned_data.get('email'))
                    participant = Participant.objects.create(
                        name=form.cleaned_data.get('name'),
                        email=form.cleaned_data.get('email'),
                        phone=form.cleaned_data.get('phone'),
                        gender = form.cleaned_data.get('gender'),
                        dob=form.cleaned_data.get('dob'),
                        college=form.cleaned_data.get('college'),)
                    
                    participant.save()
                return redirect('participant_dashboard')
            else:
                return render(request, 'portal/registration.html', {'error': 'Email verification failed. Please try again.'})
        except User.DoesNotExist:
            return render(request, 'portal/verify_email_prompt.html', {'error': 'Invalid verification token'})
    return render(request, 'portal/verify_email_prompt.html')

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
    form = TeamForm(request.POST or None, initial={'event': match.event}, user=request.user)
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
        matches = Match.objects.filter(teams__in=teams).distinct()
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
    colleges = College.objects.filter(team__event=event).distinct()
    participants = Participant.objects.filter(team__event=event)  # Default value for participants
    feedbacks = FeedBack.objects.filter(event=event).distinct()
    print(colleges)
    # Initialize score as None
    score = None

    for match in matches:
        if event.name_of_sports == 'Cricket':
            score = CricketScore.objects.filter(match=match).first()
        elif event.name_of_sports == 'Football':
            score = FootballScore.objects.filter(match=match).first()
        elif event.name_of_sports == 'Badminton':
            score = BadmintonScore.objects.filter(match=match).first()
        elif event.name_of_sports in ['Athletics-100m', 'Athletics-200m']:
            score = SingleScoringForAthletics.objects.filter(match=match, event=event).first()
        elif event.name_of_sports == 'Swimming':
            score = SingleScoringForSwimming.objects.filter(match=match, event=event).first()

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
            participants = Participant.objects.filter(college__name=filter_value, team__event=event)
        elif filter_by == 'gender':
            participants = Participant.objects.filter(gender=filter_value, team__event=event)
        else:
            participants = Participant.objects.filter(team__event=event).distinct()
        
        college_filter_by = request.GET.get('college_filter_by')
        college_filter_value = request.GET.get('college_filter_value')
        if college_filter_by == 'name':
            colleges = College.objects.filter(name=college_filter_value, participant__team__event=event).distinct
        elif college_filter_by == 'address':
            colleges = College.objects.filter(address=college_filter_value, participant__team__event=event).distinct
        elif college_filter_by == 'pincode':
            colleges = College.objects.filter(pincode=college_filter_value, participant__team__event=event).distinct
        else:
            colleges = College.objects.filter(participant__team__event=event).distinct()
    context = {
        'score': score,  # Ensure score is always defined
        'event': event,
        'matches': matches,
        'colleges': colleges,
        'participants': participants,
        'feedbacks': feedbacks,
    }
    return render(request, 'portal/eventDetails.html', context)

@login_required(login_url='account_login')
def college_members(request, college_id, event_id):
    event = Event.objects.get(id=event_id)
    college = College.objects.get(id=college_id)
    team = Team.objects.get(college=college, event=event)
    print(team)
    participants = team.participants.all()
    context = {
        'team': team,
        'college': college,
        'participants': participants,
    }
    return render(request, 'portal/collegeMembers.html', context)
@login_required(login_url='account_login')
def event_view(request):
    teams = Team.objects.filter(participants__email=request.user.email).distinct() 

    context = {
        'teams': teams,
    }
    return render(request, 'portal/eventView.html', context)
@login_required(login_url='account_login')
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
    match = Match.objects.get(id=match_id)
    event = match.event
    if request.method == 'POST':
        form = TeamForm(request.POST, event=event, user=request.user)
        if form.is_valid():
            event_form = form.cleaned_data['event']
            if event_form != event:
                return redirect(request.path_info)
            team = form.cleaned_data['team']
            if team.max_size < event.min_size:
                return redirect(request.path_info)
            match.addTeam(team)
            match.save()
            return redirect('match_details', match_id=match.id)
    else:
        form = TeamForm(event=event, user=request.user)

    return render(request, 'portal/addTeam.html', {'form': form})
@login_required(login_url='account_login')
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
@login_required(login_url='account_login')
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

def update_scores(request, match_id):
    match = Match.objects.get(id=match_id)
    event = match.event
    if event.name_of_sports == 'Cricket':
        form = CricketScoring(request.POST or None, match=match)
    elif event.name_of_sports == 'Football':
        form = FootballScoring(request.POST or None, match=match)
    elif event.name_of_sports == 'Badminton':
        form = BadmintonScoring(request.POST or None, match=match)
    elif event.name_of_sports in ['Athletics-100m', 'Athletics-200m']:
        form = SingleScoringForAthleticsForm(request.POST or None, event=event)
        formset = AthleticsScoreFormSet(request.POST or None, queryset=SingleScoringForAthletics.objects.filter(match=match))

        if form.is_valid() and formset.is_valid():
            single_score = form.save(commit=False)
            single_score.match = match
            single_score.event = event
            single_score.save()

            instances = formset.save(commit=False)
            for instance in instances:
                instance.match = match
                instance.event = event
                instance.save()
        else:
            return render(request, 'portal/update_scores.html', {'match': match, 'form': form, 'formset': formset})
    else:
        form = None

    if request.method == 'POST' and form is not None:
        if form.is_valid():
            intial_points = 0
            if event.name_of_sports == 'Cricket':
                team1_score = form.cleaned_data['team1_score']
                team2_score = form.cleaned_data['team2_score']
                team1 = form.cleaned_data['team1']
                team2 = form.cleaned_data['team2']
                team1_overs = form.cleaned_data['team1_overs']
                team1_wickets = form.cleaned_data['team1_wickets']
                team2_overs = form.cleaned_data['team2_overs']
                team2_wickets = form.cleaned_data['team2_wickets']
                team1_verdict = form.cleaned_data['verdict_for_team1']
                cricket_score=CricketScore.objects.create(
                    event=event,
                    match=match,
                    team1=team1,
                    team2=team2,
                    team1_score=team1_score,
                    team2_score=team2_score,
                    team1_overs=team1_overs,
                    team1_wickets=team1_wickets,
                    team2_overs=team2_overs,
                    team2_wickets=team2_wickets,
                    verdict_for_team1=team1_verdict
                )
                cricket_score.save()
            elif event.name_of_sports == 'Football':
                team1_goals = form.cleaned_data['team1_goals']
                team2_goals = form.cleaned_data['team2_goals']
                team1 = form.cleaned_data['team1']
                team2 = form.cleaned_data['team2']
                team1_verdict = form.cleaned_data['verdict_for_team1']
                if team1_verdict == 'Win':
                    team2_verdict = 'Loss'
                elif team1_verdict == 'Loss':
                    team2_verdict = 'Win'
                else:
                    team2_verdict = 'Tie'
                football_score=FootballScore.objects.create(
                    event=event,
                    match=match,
                    team1=team1,
                    team2=team2,
                    team1_goals=team1_goals,
                    team2_goals=team2_goals,
                    verdict_for_team1=team1_verdict
                )
                football_score.save()
            elif event.name_of_sports == 'Badminton':
                team1_sets_won = form.cleaned_data['team1_sets_won']
                team2_sets_won = form.cleaned_data['team2_sets_won']
                team1 = form.cleaned_data['team1']
                team2 = form.cleaned_data['team2']
                team1_verdict = form.cleaned_data['verdict_for_team1']
                badminton_score=BadmintonScore.objects.create(
                    event=event,
                    match=match,
                    team1=team1,
                    team2=team2,
                    team1_sets_won=team1_sets_won,
                    team2_sets_won=team2_sets_won,
                    verdict_for_team1=team1_verdict
                )
                badminton_score.save()
            elif event.name_of_sports in ['Athletics-100m', 'Athletics-200m']:
                if formset.is_valid():
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.match = match
                        instance.event = event
                        instance.save()
                        single_score = SingleScoringForAthletics.objects.create(
                            match=match,
                            event=event,
                            participant=instance.participant,
                            score=instance.score
                        )
                        single_score.save()
            else:
                return render(request, 'portal/update_scores.html', {'match': match, 'form': form, 'error': 'Invalid event type.'})
            return redirect('match_details', match_id=match.id)
    return render(request, 'portal/update_scores.html', {'match': match,'form': form})
@login_required(login_url='account_login')
def view_scores(request):
    participant = Participant.objects.get(email=request.user.email)
    teams = Team.objects.filter(participants=participant)
    college_teams = Team.objects.filter(college=participant.college)

    participant_matches = Match.objects.filter(teams__in=teams).distinct()
    college_matches = Match.objects.filter(teams__in=college_teams).distinct()

    participant_scores = []
    college_scores = []
    for match in participant_matches:
        if match.event.name_of_sports == 'Cricket':
            score = CricketScore.objects.filter(match=match).first()
        elif match.event.name_of_sports == 'Football':
            score = FootballScore.objects.filter(match=match).first()
        elif match.event.name_of_sports == 'Badminton':
            score = BadmintonScore.objects.filter(match=match).first()
        else:
            score = None

        if score:
            participant_scores.append(score)
        
    for match in participant_matches:
        if match.event.name_of_sports == 'Cricket':
            score = CricketScore.objects.filter(match=match).first()
        elif match.event.name_of_sports == 'Football':
            score = FootballScore.objects.filter(match=match).first()
        elif match.event.name_of_sports == 'Badminton':
            score = BadmintonScore.objects.filter(match=match).first()
        else:
            score = None
        print(score)
        if score:
            college_scores.append(score)
    p_range = range(len(participant_matches))
    c_range = range(len(college_matches))
    print(college_matches)
    context = {
        'p_range': p_range,
        'c_range': c_range,
        'participant_matches': participant_matches,
        'college_matches': college_matches,
        'participant_scores': participant_scores,
        'college_scores': college_scores,
    }
    return render(request, 'portal/view_scores.html', context)

def participant_feedback(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')
        participant = Participant.objects.get(email=request.user.email)
        feedback_obj = FeedBack.objects.create(event=event, participant=participant, feedback=feedback, rating=rating)
        feedback_obj.save()
        return redirect('events')
    return render(request, 'portal/feedback.html', {'event': event})

def kick_participant(request, participant_id, team_id):
    team = Team.objects.get(id=team_id)
    participant = Participant.objects.get(id=participant_id)
    if request.method == 'POST':
        team.removePlayer(participant)
        team.save()
        return redirect('events')