from django.contrib import admin
from django.urls import path
from . import views
from django.urls.conf import include

urlpatterns=[
        path('accounts/',include('allauth.urls')),
        path('',views.home,name='home'),
        path('prelogin/',views.login,name='login'),
        path('candidate/',views.candidate,name='candidate'),
        path('candidateRedirect/',views.candidateRedirect,name='candidate_redirect'),
]