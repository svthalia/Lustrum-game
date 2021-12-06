from authlib.integrations.base_client import OAuthError
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.db.utils import OperationalError

from frontend.models import User
from frontend.oauth import oauth


class ConcrexitBackend(BaseBackend):
    def authenticate(self, request, token=None):
        try:
            resp = oauth.getOAuth().thalia.get('', token=token)
        except OAuthError:
            return None
        newUser = resp.json()
        if resp.ok:
            try:
                user = User.objects.get(pk=newUser['pk'])

                # Check if user changed
                change = False
                if user.name != newUser['profile']['display_name']:
                    user.name = newUser['profile']['display_name']
                    change = True
                elif user.profilePicture != newUser['profile']['photo']['full']:
                    user.profilePicture = newUser['profile']['photo']['full']
                    change = True

                if change:
                    user.save()

            except User.DoesNotExist:
                user = User.objects.create(pk=newUser['pk'], name=newUser['profile']['display_name'],
                                           profilePicture=newUser['profile']['photo']['full'])
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
