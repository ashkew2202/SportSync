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
    match_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    match_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    venue = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue'})
    )
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Match
        fields = ['match_date', 'match_time', 'venue', 'team', 'event']