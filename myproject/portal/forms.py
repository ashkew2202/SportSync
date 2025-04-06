from django import forms
from .models import Participant, Organizer, Match, Event, Team, College

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
        queryset=Event.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    teams = forms.ModelChoiceField(
        queryset=Team.objects.filter(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Team
        fields = ['event', 'teams']