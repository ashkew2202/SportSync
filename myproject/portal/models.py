from django.db import models
from django.contrib.auth import get_user
from django.contrib.auth.models import User, AbstractUser
import random
import string
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AnonymousUser


class College(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    def __str__(self):
        return self.name

class BannedParticipants(models.Model):
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.participant} banned from {self.team}"

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
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        request = kwargs.get('request')  # Get the request object
        if request and hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            self.email = request.user.email  # Use the email from the logged-in user
        super(Participant, self).save(*args, **kwargs)

    def banPlayer(self, event):
        teams = Team.objects.filter(event=event, college=self.college)
        for team in teams:
            team.removePlayer(self)
        banned = BannedParticipants(participant=self, team=team)
        banned.save()
        print(f"Banned {self} from {event}")
        return self
        

    def __str__(self):
        return self.name

class Organizer(AbstractUser):
    name = models.CharField(max_length=100)
    
    def generate_random_password(length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

    password = models.CharField(max_length=100, default=generate_random_password)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    organizerCompany = models.CharField(max_length=100)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='organizer_groups',  # Add a unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='organizer_permissions',  # Add a unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def register_organizer_as_user(self):
        user = User.objects.create(username=self.name, email=self.email, password=self.password)
        user.save()
        return user

    def __str__(self):
        return self.name
        
class Event(models.Model):
    SPORT_CHOICES= [
        ('Cricket', 'Cricket'),
        ('Football', 'Football'),
        ('Badminton', 'Badminton'),
        ('Athletics-100m', 'Athletics-100m'),
        ('Athletics-200m', 'Athletics-200m'),
    ]
    GENDER_CHOICES = [
        ('Men','Men'),
        ('Women','Women'),
        ('Mixed','Mixed'),
    ]
    SCORE_CHOICES = [
        ('Runs', 'Runs'),
        ('Goals', 'Goals'),
        ('Points', 'Points'),
        ('Time', 'Time'),
    ]
    name_of_sports = models.CharField(max_length=100, choices=SPORT_CHOICES)
    scoring_system = models.CharField(max_length=50, choices=SCORE_CHOICES)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    organizer=models.ForeignKey(Organizer, on_delete=models.CASCADE)
    max_size = models.IntegerField()
    min_size = models.IntegerField()

    def __str__(self):
        return f'{self.name_of_sports}-{self.gender}'

    @staticmethod
    def check_one_team_per_college():
        teams = Team.objects.values('college').distinct()
        for team in teams:
            if team['team_count'] > 1:
                return False
        return True

class Team(models.Model):
    captain=models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='captain')
    college=models.ForeignKey(College, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Participant)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='team_event', null=True, blank=True)
    def addParticipant(self, participant):
        if self.participants.count() < self.max_size:
            self.participants.add(participant)
            print(f"Added {participant} to {self}")
        else:
            raise ValidationError("Cannot add more participants, team is full.")
        
    def clean(self):
        if self.pk and self.participants.exists():  # Ensure the team has been saved
            college = self.participants.first().college
            if not all(participant.college == college for participant in self.participants.all()):
                raise ValidationError("All participants must be from the same college.")
    max_size = models.IntegerField()

    def checkCaptain(self, participant):
        return participant == self.captain
    
    def removePlayer(self, participant):
        self.participants.remove(participant)
        print(f"Removed {participant} from {self}")
        return self

    def __str__(self):
        return f"Team for {self.event.name_of_sports} organized by {self.event.organizer.name} ({self.event.gender}), College: {self.college.name}, Captain: {self.captain.name}"

class Match(models.Model):
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=100)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Scheduled', choices=[
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ])
    def addTeam(self, team):
        if team.event != self.event:
            raise ValidationError("All teams in a match must belong to the same event.")
        self.teams.add(team)
        print(f"Added {team} to match at {self.venue}")

    def checkTeam(self, team):
        if team.participants.count() < team.event.min_size:
            return False
        return True

    def __str__(self):
        return self.organizer.name + " " + str(self.date) + " " + str(self.time) + " " + self.venue

class CricketScore(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_score')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_score')
    team1_score = models.IntegerField()
    team2_score = models.IntegerField()
    team1_overs = models.IntegerField()
    team2_overs = models.IntegerField()
    team1_wickets = models.IntegerField()
    team2_wickets = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    choices = [
        ('Win', 'Win'),
        ('Loss', 'Loss'),
        ('Tie', 'Tie'),
        ('No Result', 'No Result'),
    ]
    verdict_for_team1 = models.CharField(max_length=20, choices=choices)

    def __str__(self):
        return f"Match: {self.match}, Team1 Score: {self.team1_score}, Team2 Score: {self.team2_score}"

class SingleScoringForAthletics(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    scores = models.ManyToManyField(Participant, through='portal.AthleticsScore')
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return f"Event: {self.event}, Match: {self.match}"

class SingleScoringForSwimming(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    scores = models.ManyToManyField(Participant, through='SwimmingScore')
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return f"Event: {self.event}, Match: {self.match}"

class SwimmingScore(models.Model):
    scoring = models.ForeignKey(SingleScoringForSwimming, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    verdict_choices = [
        ('Qualified', 'Qualified'),
        ('Disqualified', 'Disqualified'),
        ('Did Not Finish', 'Did Not Finish'),
    ]
    verdict = models.CharField(max_length=20, choices=verdict_choices, null=True, blank=True, default='Did Not Finish')
    time = models.DurationField(null=True, blank=True)  
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    position = models.IntegerField(null=True, blank=True)

class AthleticsScore(models.Model):
    scoring = models.ForeignKey(SingleScoringForAthletics, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    verdict_choices = [
        ('Qualified', 'Qualified'),
        ('Disqualified', 'Disqualified'),
        ('Did Not Finish', 'Did Not Finish'),
    ]
    verdict = models.CharField(max_length=20, choices=verdict_choices, null=True, blank=True, default='Did Not Finish')
    time = models.DurationField(null=True, blank=True)  
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Event: {self.event}, Participant: {self.participant}, Time: {self.time}, Distance: {self.distance}, Position: {self.position}"

class BadmintonScore(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='badminton_scores')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='badminton_scores2')
    team1_sets_won = models.IntegerField(default=0)  # Number of sets won by team1
    team2_sets_won = models.IntegerField(default=0)  # Number of sets won by team2
    team1_points = models.IntegerField(default=0)  # Points awarded for team1
    team2_points = models.IntegerField(default=0)  # Points awarded for team2
    verdict_choices = [
        ('Win', 'Win'),
        ('Loss', 'Loss'),
    ]
    verdict_for_team1 = models.CharField(max_length=20, choices=verdict_choices, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically calculate points based on the verdict
        if self.verdict_for_team1 == 'win':
            self.team1_points = 2  # 3 points for a win
            self.team2_points = 0  # No points for a loss
        elif self.verdict_for_team1 == 'draw':
            self.team1_points = 1  # 1 point for a draw
            self.team2_points = 1  # 1 point for a draw
        else:
            self.team1_points = 0  # No points for a loss
            self.team2_points = 2  # 3 points for a win
        super(BadmintonScore, self).save(*args, **kwargs)

    def __str__(self):
        return f"Match: {self.match}, Team1 Sets Won: {self.team1_sets_won}, Team2 Sets Won: {self.team2_sets_won}, Verdict for Team1: {self.verdict_for_team1}"

class FootballScore(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='football_scores1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='football_scores2')
    team1_goals = models.IntegerField(default=0)  # Goals scored by team1
    team2_goals = models.IntegerField(default=0)  # Goals scored by team2
    team1_points = models.IntegerField(default=0)  # Points awarded for team1
    team2_points = models.IntegerField(default=0)  # Points awarded for team2
    verdict_choices = [
        ('Win', 'Win'),
        ('Loss', 'Loss'),
        ('Draw', 'Draw'),
    ]
    verdict_for_team1 = models.CharField(max_length=20, choices=verdict_choices, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically calculate points based on the verdict
        if self.verdict_for_team1 == 'win':
            self.team1_points = 3  # 3 points for a win
            self.team2_points = 0  # No points for a loss
        elif self.verdict_for_team1 == 'draw':
            self.team1_points = 1  # 1 point for a draw
            self.team2_points = 1  # 1 point for a draw
        else:
            self.team1_points = 0  # No points for a loss
            self.team2_points = 3  # 3 points for a win
        super(FootballScore, self).save(*args, **kwargs)

    def __str__(self):
        return f"Match: {self.match}, Team: {self.team}, Goals: {self.goals}, Verdict: {self.verdict}"
    
class FeedBack(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.IntegerField()
    image = models.ImageField(upload_to='feedback_images/', null=True, blank=True)
    def __str__(self):
        return f'The feedback from {self.participant} for {self.event} is {self.feedback} and rating is {self.rating}'

