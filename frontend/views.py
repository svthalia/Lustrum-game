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
            context['user_name'] = user.name
            context['user_profile_picture'] = user.profilePicture
            try:
                player = Player.objects.get(user=user)
                try:
                    context['target_name'] = player.target.name
                    context['target_picture'] = player.target.profilePicture
                    context['finished'] = player.target == player.user
                except AttributeError:
                    context['target_name'] = False
                    context['target_picture'] = False
                context['player_life_status'] = player.is_dead
                context['player_grey'] = "grayscale" if player.is_dead else ""
                try:
                    murder_on_user = Murder.objects.get(victim=player, agreed_on=False)
                    context['murder_confirmation'] = murder_on_user.murderer.user.name
                except Murder.DoesNotExist:
                    pass
                try:
                    Murder.objects.get(murderer=player, agreed_on=False)
                    context['murder_waiting'] = "true"
                except Murder.DoesNotExist:
                    context['murder_waiting'] = "false"
                context['user_score'] = player.get_score()
            except (Player.DoesNotExist, AttributeError):
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
                target_player = Player.objects.get(user=user)
                if target_player is not None:
                    try:
                        murder = Murder.objects.get(victim=target_player, agreed_on=False)
                        murder.agreed_on = True
                        murder.save()
                        target_player.is_dead = True
                        target_player.save()
                        try:
                            killer_player = Player.objects.get(user=murder.murderer.user)
                            killer_player.target = target_player.target
                            killer_player.save()
                            response_data["error"] = False
                            return HttpResponse(json.dumps(response_data), content_type='application/json')
                        except Player.DoesNotExist:
                            response_data["error"] = True
                            response_data["reason"] = "No new target"
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
                    if target is not None and not player.is_dead:
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


def kill_cancel(request):
    response_data = {}

    if 'user' in request.session:
        user = authenticate(request, token=request.session["user"]["token"])
        if user is not None:
            try:
                murderer = Player.objects.get(user=user)
                try:
                    murder = Murder.objects.get(murderer=murderer, agreed_on=False)
                    murder.delete()
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
