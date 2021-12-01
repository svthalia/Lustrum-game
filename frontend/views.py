import os
from authlib.integrations.django_client import OAuth
from django.shortcuts import render, redirect
from django.urls import reverse

from frontend.models import User, Player

oauth = OAuth()
oauth.register(
    name="thalia",
    client_id=os.environ.get('CLIENT_ID'),
    access_token_url='https://staging.thalia.nu/user/oauth/token/',
    access_token_params=None,
    refresh_token_url=None,
    authorize_url='https://staging.thalia.nu/user/oauth/authorize',
    api_base_url='https://staging.thalia.nu/api/v2/members/me/',
    client_kwargs={'scope': "profile:read", 'grant_type': "authorization_code"}
)


def index(request):
    context = {}

    return render(request, 'base.html', context)


def login(request):
    redirect_uri = request.build_absolute_uri(reverse('auth'))
    return oauth.thalia.authorize_redirect(request, redirect_uri)


def auth(request):
    token = oauth.thalia.authorize_access_token(request)
    resp = oauth.thalia.get('', token=token)
    user = resp.json()
    query = User.objects.filter(pk=user['pk'])
    if query.count() == 0:
        User.objects.create(id=user['pk'], name=user['profile']['display_name'], profilePicture=user['profile']['photo']['full'])
        request.session['user'] = {'name': user['profile']['display_name'], 'profilePicture': user['profile']['photo']['full'], 'isPlayer': False}
    elif query.count() == 1:
        # TODO: Check if name or pf has changed, then also update in our db
        #player_query = Player.objects.filter(user=query.first())
        #if player_query.count() == 0:
         #   print("NOTHIONG")
        request.session['user'] = {'name': user['profile']['display_name'], 'profilePicture': user['profile']['photo']['full'], 'isPlayer': False}
        # else:
        #     print("ELSE", player_query.first().victim.get().count())
        #     request.session['user'] = {'name': user['profile']['display_name'],
        #                                'profilePicture': user['profile']['photo']['full'], 'isPlayer': True,
        #                                'victimName': player_query.first().victim.user.name,
        #                                'victimPicture': player_query.first().victim.user.profilePicture,
        #                                }
    return redirect('/')


def logout(request):
    request.session.pop('user', None)
    return redirect('/')
