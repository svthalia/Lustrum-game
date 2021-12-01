import os
from authlib.integrations.django_client import OAuth
from django.shortcuts import render, redirect
from django.urls import reverse

from frontend.models import User

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
    print(token, resp)
    # if resp.status != 404:
    print(resp.json())
    user = resp.json()
    print(User.objects.filter(pk=user['pk']))
    if User.objects.filter(pk=user['pk']).count() == 0:
        print("CREATE")
        User.objects.create(id=user['pk'], name=user['profile']['display_name'], profilePicture=user['profile']['photo']['full'])
        request.session['user'] = {'name': user['profile']['display_name'], 'profilePicture': user['profile']['photo']['full']}
    return redirect('/')


def logout(request):
    request.session.pop('user', None)
    return redirect('/')
