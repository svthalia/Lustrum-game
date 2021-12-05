import os

from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.urls import reverse

from frontend.models import Player
from frontend.oauth import oauth


def index(request):
    context = {}

    if 'user' in request.session:
        user = authenticate(request, token=request.session["user"]["token"])
        if user is not None:
            try:
                player = Player.objects.get(user=user)
                if player.target is not None:
                    context = {'target_name': player.target.name, 'target_picture': player.target.profilePicture}
            except Player.DoesNotExist:
                pass
        else:
            request.session.pop('user', None)

    return render(request, 'base.html', context)


def login(request):
    redirect_uri = request.build_absolute_uri(reverse("auth"))
    return oauth.getOAuth().thalia.authorize_redirect(request, redirect_uri)


def auth(request):
    token = oauth.getOAuth().thalia.authorize_access_token(request)
    resp = oauth.getOAuth().thalia.get('', token=token)
    user = resp.json()

    request.session['user'] = {'id': user['pk'], 'name': user['profile']['display_name'],
                               'profilePicture': user['profile']['photo']['full'], 'token': token}

    return redirect('/')


def logout(request):
    request.session.pop('user', None)
    return redirect('/')

