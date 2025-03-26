from django.db import models
from django.contrib.auth import get_user
import random
import string
from django.db.models import Count
from django.core.exceptions import ValidationError

class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField()
    phone = models.CharField(max_length=10)
    college = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        user = get_user(kwargs.get('request'))
        self.email = user.email if user else self.email
        super(Participant, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Organizer(models.Model):
    name=models.CharField(max_length=100)
    def generate_random_password(length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

    password = models.CharField(max_length=100, default=generate_random_password)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    organizerCompany=models.CharField(max_length=100)

class Team(models.Model):
    college=models.CharField(max_length=100)
    participants = models.ManyToManyField(Participant)
    def clean(self):
        if self.participants.exists():
            college = self.participants.first().college
            if not all(participant.college == college for participant in self.participants.all()):
                raise ValidationError("All participants must be from the same college.")
    max_size = models.IntegerField()

    def __str__(self):
        return f"Team from {self.college} with max size {self.max_size}"

class Event(models.Model):
    name_of_sports=models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('X', 'Mixed'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name_of_sports

    @staticmethod
    def check_one_team_per_college():
        teams = Team.objects.values('college').annotate(team_count=Count('id'))
        for team in teams:
            if team['team_count'] > 1:
                return False
        return True

class Match(models.Model):
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=100)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team)
    event=models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.name