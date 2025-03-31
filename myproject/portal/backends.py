from django.contrib.auth.backends import BaseBackend
from .models import Organizer

class OrganizerBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            organizer = Organizer.objects.get(name=username)
            return organizer
        except Organizer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Organizer.objects.get(pk=user_id)
        except Organizer.DoesNotExist:
            return None