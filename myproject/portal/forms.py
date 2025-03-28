from django import forms
from .models import Participant, Organizer

class RegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # Add a date picker widget
    phone = forms.CharField(max_length=10)
    college = forms.CharField(max_length=100)

    class Meta:
        model = Participant
        fields = '__all__'

class OrganizerLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    class Meta:
        model = Organizer
        fields = ['name', 'password']