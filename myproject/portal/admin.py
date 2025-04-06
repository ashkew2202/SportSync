from django.contrib import admin
from .models import Match,Event, Organizer, Participant, Team, BannedParticipants, College, CricketScore, FootballScore, BadmintonScore, AthleticsScore

admin.site.register(Match)
admin.site.register(Event)
admin.site.register(Organizer)
admin.site.register(Participant)
admin.site.register(Team)
admin.site.register(BannedParticipants)
admin.site.register(College)
admin.site.register(CricketScore)
admin.site.register(FootballScore)
admin.site.register(BadmintonScore)
admin.site.register(AthleticsScore)
