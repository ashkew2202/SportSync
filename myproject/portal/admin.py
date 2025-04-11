from django.contrib import admin
from .models import Match, Event, Organizer, Participant, Team, BannedParticipants, College, CricketScore, FootballScore, BadmintonScore, AthleticsScore, SingleScoringForAthletics, SingleScoringForSwimming, SwimmingScore

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

class SingleScoringForAthleticsInline(admin.TabularInline):
    model = AthleticsScore
    extra = 1 

class AthleticScoringAdmin(admin.ModelAdmin):
    inlines = [SingleScoringForAthleticsInline]

admin.site.register(SingleScoringForAthletics, AthleticScoringAdmin)

class SwimmingInline(admin.TabularInline):
    model = SwimmingScore
    extra = 1 

class SwimmingScoringAdmin(admin.ModelAdmin):
    inlines = [SwimmingInline]

admin.site.register(SingleScoringForSwimming, SwimmingScoringAdmin)
