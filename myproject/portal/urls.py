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
]