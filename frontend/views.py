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
                    pass
                context['player_life_status'] = player.is_dead
                context['player_grey'] = "grayscale" if player.is_dead else ""

                murder_on_user = Murder.objects.filter(victim=player, agreed_on=False).first()
                if murder_on_user is not None:
                    context['murder_confirmation'] = murder_on_user.murderer.user.name

                waiting = Murder.objects.filter(murderer=player, agreed_on=False).first()

                if waiting is not None:
                    context['murder_waiting'] = "true"
                else:
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


def takeScore(elem):
    return elem['score']


def leaderboard(request):
    context = {}
    if 'user' in request.session:
        user = authenticate(request, token=request.session["user"]["token"])
        if user is not None:
            context['user_name'] = user.name
            context['user_profile_picture'] = user.profilePicture
            murders = Murder.objects.all()
            players = Player.objects.all()

            scores = []
            for player in players:
                scores.append({"pk": player.user.pk, "name": player.user.name, "score": 0})
            for murder in murders:
                if murder.agreed_on:
                    for x in range(len(scores)):
                        if scores[x]['pk'] == murder.murderer.user.pk:
                            scores[x]['score'] = scores[x]['score'] + 1
                        elif scores[x]['pk'] == murder.victim.user.pk:
                            scores[x]['score'] = scores[x]['score'] - 2
            scores.sort(key=takeScore, reverse=True)
            context['scores'] = scores
        else:
            request.session.pop('user', None)
    return render(request, 'leaderboard/base.html', context)


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
                    murder = Murder.objects.filter(victim=target_player, agreed_on=False).first()
                    if murder is not None:
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
                    else:
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

                murder = Murder.objects.filter(murderer=murderer, agreed_on=False).first()
                if murder is not None:
                    murder.delete()
                    response_data["error"] = False
                    return HttpResponse(json.dumps(response_data), content_type='application/json')
                else:
                    response_data["error"] = True
                    response_data["reason"] = "No such murder"
                    return HttpResponse(json.dumps(response_data), content_type='application/json')
            except Player.DoesNotExist:
                response_data["error"] = True
                response_data["reason"] = "Murderer does not exist"
                return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            request.session.pop('user', None)
            response_data["error"] = True
            response_data["reason"] = "Wrong auth"
            return HttpResponse(json.dumps(response_data), content_type='application/json')

    response_data["error"] = True
    response_data["reason"] = "No authentication"
    return HttpResponse(json.dumps(response_data), content_type='application/json')
