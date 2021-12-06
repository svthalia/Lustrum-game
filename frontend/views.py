import json
import os

from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from frontend.models import Player, Murder
from frontend.oauth import oauth


def index(request):
    context = {}

    if 'user' in request.session:
        user = authenticate(request, token=request.session["user"]["token"])
        if user is not None:
            try:
                player = Player.objects.get(user=user)
                if player.target is not None:
                    try:
                        murder = Murder.objects.get(victim=player, agreed_on=False)
                        context = {'target_name': player.target.name, 'target_picture': player.target.profilePicture,
                                   'murder': murder.murderer.user.name}
                    except Murder.DoesNotExist:
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


def kill_confirm(request):
    response_data = {}

    if 'user' in request.session:
        user = authenticate(request, token=request.session["user"]["token"])
        if user is not None:
            try:
                target = Player.objects.get(user=user)
                if target is not None:
                    try:
                        murder = Murder.objects.get(victim=target, agreed_on=False)
                        murder.agreed_on = True
                        murder.save()
                        response_data["error"] = False
                        return HttpResponse(json.dumps(response_data), content_type='application/json')

                    except Murder.DoesNotExist:
                        response_data["error"] = True
                        response_data["reason"] = "No such murder"
                        return HttpResponse(json.dumps(response_data), content_type='application/json')
            except Player.DoesNotExist:
                response_data["error"] = True
                response_data["reason"] = "Victim does not exist"
                return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            request.session.pop('user', None)
            response_data["error"] = True
            response_data["reason"] = "Wrong auth"
            return HttpResponse(json.dumps(response_data), content_type='application/json')

    response_data["error"] = True
    response_data["reason"] = "No authentication"
    return HttpResponse(json.dumps(response_data), content_type='application/json')


def kill(request):
    response_data = {}

    if 'user' in request.session:
        user = authenticate(request, token=request.session["user"]["token"])
        if user is not None:
            try:
                player = Player.objects.get(user=user)
                if player.target is not None:
                    target = Player.objects.get(user=player.target)
                    if target is not None:
                        try:
                            Murder.objects.get(murderer=player, victim=target, agreed_on=False)
                            response_data["error"] = True
                            response_data["reason"] = "Kill already exists"
                            return HttpResponse(json.dumps(response_data), content_type='application/json')

                        except Murder.DoesNotExist:
                            Murder.objects.create(murderer=player, victim=target, agreed_on=False)
                            response_data["error"] = False
                            return HttpResponse(json.dumps(response_data), content_type='application/json')

                response_data["error"] = True
                response_data["reason"] = "No target"
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            except Player.DoesNotExist:
                response_data["error"] = True
                response_data["reason"] = "Player does not exist"
                return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            request.session.pop('user', None)
            response_data["error"] = True
            response_data["reason"] = "Wrong auth"
            return HttpResponse(json.dumps(response_data), content_type='application/json')

    response_data["error"] = True
    response_data["reason"] = "No authentication"
    return HttpResponse(json.dumps(response_data), content_type='application/json')
