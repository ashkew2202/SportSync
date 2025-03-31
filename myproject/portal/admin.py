from django.contrib import admin
from .models import Match,Event, Organizer, Participant, Team, BannedParticipants, College

admin.site.register(Match)
admin.site.register(Event)
admin.site.register(Organizer)
admin.site.register(Participant)
admin.site.register(Team)
admin.site.register(BannedParticipants)
admin.site.register(College)