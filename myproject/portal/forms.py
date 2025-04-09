from django import forms
from .models import Participant, Organizer, Match, Event, Team, College, CricketScore, FootballScore, BadmintonScore, AthleticsScore

class RegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # Add a date picker widget
    phone = forms.CharField(max_length=10)
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Participant
        fields = '__all__'

class OrganizerLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    class Meta:
        model = Organizer
        fields = ['name', 'password']

class MatchForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    venue = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue'})
    )
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Match
        fields = ['date', 'time', 'venue', 'teams', 'event']

class EventForm(forms.ModelForm):
    SPORT_CHOICES= [
        ('Cricket', 'Cricket'),
        ('Football', 'Football'),
        ('Badminton', 'Badminton'),
        ('Athletics-100m', 'Athletics-100m'),
        ('Athletics-200m', 'Athletics-200m'),
    ]
    gender_choices = [
        ('Men','Men'),
        ('Women','Women'),
        ('Mixed','Mixed'),
    ]
    scoring_system_choices = [
        ('Runs', 'Runs'),
        ('Goals', 'Goals'),
        ('Points', 'Points'),
        ('Time', 'Time'),
    ]
    name_of_sports = forms.ChoiceField(
        choices=SPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=gender_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    scoring_system = forms.ChoiceField(
        choices=scoring_system_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    max_size = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Size'})
    )
    min_size = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Size'})
    )
    class Meta:
        model = Event
        fields = ['name_of_sports', 'gender', 'scoring_system','max_size','min_size']

class TeamForm(forms.ModelForm):
    event = forms.ModelChoiceField(
        queryset=Event.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    teams = forms.ModelChoiceField(
            queryset=Team.objects.none(),
            widget=forms.Select(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['event'].queryset = Event.objects.filter(organizer=user)
        else:
            self.fields['event'].queryset = Event.objects.none()
        
        event = kwargs.pop('event', None)
        if event:
            self.fields['teams'].queryset = Team.objects.filter(event=event)
    class Meta:
        model = Team
        fields = ['event', 'teams']

class CricketScoring(forms.ModelForm):
    team1 = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team 1'})
    )
    team1_score = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 1 Runs'})
    )
    team1_wickets = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 1 Wickets'})
    )
    team1_overs = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 1 Overs'}),
        max_digits=4,
        decimal_places=1
    )
    team2 = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team 2'})
    )
    team2_score = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 2 Runs'})
    )
    
    team2_wickets = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 2 Wickets'})
    )
    
    team2_overs = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 2 Overs'}),
        max_digits=4,
        decimal_places=1
    )
    verdict_for_team1 = forms.ChoiceField(
        choices=[('Win', 'Win'), ('Loss', 'Loss'), ('Tie', 'Tie')],
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Verdict'})
    )
    def __init__(self, *args, **kwargs):
        match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        if match:
            self.fields['team1'].queryset = match.teams.all()
            self.fields['team2'].queryset = match.teams.all()

    class Meta:
        model = CricketScore
        fields = ['team1', 'team1_score', 'team1_wickets', 'team1_overs', 'team2', 'team2_score', 'team2_wickets', 'team2_overs', 'verdict_for_team1']

class FootballScoring(forms.ModelForm):
    team1 = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team 1'})
    )
    team1_goals = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 1 Goals'})
    )
    team1_points = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 1 Points'})
    )
    team2 = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team 2'})
    )
    team2_goals = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 2 Goals'})
    )
    team2_points = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 2 Points'})
    )
    def __init__(self, *args, **kwargs):
        match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        if match:
            self.fields['team1'].queryset = match.teams.all()
            self.fields['team2'].queryset = match.teams.all()

    verdict_for_team1 = forms.ChoiceField(
        choices=[('Win', 'Win'), ('Loss', 'Loss'), ('Draw', 'Draw')],
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Verdict'})
    )
    class Meta:
        model = FootballScore
        fields = ['team1', 'team1_goals', 'team2', 'team2_goals', 'verdict_for_team1']

class BadmintonScoring(forms.ModelForm):
    team1 = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team 1'})
    )
    team1_sets_won = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 1 Sets Won'})
    )
    team1_points = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 1 Points'})
    )
    team2 = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team 2'})
    )
    team2_sets_won = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 2 Sets Won'})
    )
    team2_points = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team 2 Points'})
    )
    verdict_for_team1 = forms.ChoiceField(
        choices=[('Win', 'Win'), ('Loss', 'Loss'), ('Draw', 'Draw')],
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Verdict'})
    )
    def __init__(self, *args, **kwargs):
        match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        if match:
            self.fields['team1'].queryset = match.teams.all()
            self.fields['team2'].queryset = match.teams.all()
    class Meta:
        model = BadmintonScore
        fields = ['team1', 'team1_points','team1_sets_won', 'team2', 'team2_points','team2_sets_won', 'verdict_for_team1']