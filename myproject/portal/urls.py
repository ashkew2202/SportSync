from django.contrib import admin
from django.urls import path
from . import views
from django.urls.conf import include

urlpatterns=[
        path('accounts/',include('allauth.urls')),
        path('',views.home,name='home'),
        path('registration/',views.register,name='register'),
        path('organizer_login/',views.ologin,name='organizer_login'),
        path('prelogin/',views.prelogin,name='prelogin'),
        path('profile/',views.profile,name='account_profile'),
        path('organizer_dashboard/',views.organizer_entry,name='organizer_dashboard'),
        path('match_details/<int:match_id>/',views.match_details,name='match_details'),
        path('update_details/<int:match_id>/',views.update_match,name='update_details'),
        path('delete_match/<int:match_id>/',views.delete_match,name='delete_match'),
        path('add_match/',views.addMatch,name='add_match'),
        path('participant_dashboard/',views.participant_entry,name='participant_dashboard'),
        path('addEvent/', views.add_event, name='add_event'),
        path('eventDetails/<int:event_id>/',views.event_details, name='event_details'),
        path('collegeDetails/<int:college_id>/<int:event_id>/',views.college_members, name='college_details'),
        path('events/',views.event_view,name='events'),
        path('register_participant/<int:event_id>',views.register_participant,name='register_participant'),
        path('banParticipant/<int:participant_id>/<int:team_id>/',views.ban_participant,name='ban_participant'),
        path('addTeam/<int:match_id>/',views.addTeam,name='add_team'),
        path('teamDetails/<int:team_id>/',views.team_details,name='team_details'),
        path('addTeamMember/<int:team_id>/',views.addTeamMembers,name='add_team_member'),
        path('updateStatus/<int:match_id>/',views.update_status,name='update_status'),
        path('updateScore/<int:match_id>/',views.update_scores,name='update_scores'),
        path('viewScores/', views.view_scores, name='view_scores'),
        path('feedback/<int:event_id>/',views.participant_feedback,name='feedback'),
        path('verify_participant/',views.verify_email_prompt, name='verify_participant'),
        path('kick_participant/<int:participant_id>/<int:team_id>/',views.kick_participant,name='kick_participant'),
        path('oleaderboard/<int:event_id>',views.oleaderboard,name='oleaderboard'),
        path('export_to_excel/<int:event_id>/',views.add_match_thru_excel,name='export_to_excel'),
        path('college_events/<int:college_id>/',views.college_events,name='college_events'),
]