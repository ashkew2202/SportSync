from allauth.account.forms import SignupForm
from django import forms
class MyCustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['option'] = forms.ChoiceField(
            choices=[('candidate', 'Candidate'), ('organizer', 'Organizer')],
            widget=forms.RadioSelect,
            label="Select your role"
        )
    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        user.option = self.cleaned_data['option']
        ...
        