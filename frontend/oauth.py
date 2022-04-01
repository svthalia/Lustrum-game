import os

from authlib.integrations.django_client import OAuth


class Oauth:
    oauth = None

    def __init__(self):
        self.oauth = OAuth()
        self.oauth.register(
            name="thalia",
            client_id=os.environ.get('CLIENT_ID'),
            access_token_url='https://thalia.nu/user/oauth/token/',
            access_token_params=None,
            refresh_token_url=None,
            authorize_url='https://thalia.nu/user/oauth/authorize',
            api_base_url='https://thalia.nu/api/v2/members/me/',
            client_kwargs={'scope': "profile:read", 'grant_type': "authorization_code"}
        )

    def getOAuth(self):
        return self.oauth


oauth = Oauth()
