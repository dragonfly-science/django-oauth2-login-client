import logging
from time import time

from django.conf import settings
from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .utils import get_login_url

def login_redirect(request):
    request.session['next'] = request.GET.get('next', request.path)
    urldata = get_login_url()
    request.session['oauth_login_state'] = urldata['state']
    return redirect(urldata['authorization_url'])

def account_redirect(request):
    return redirect(settings.OAUTH_SERVER + '/accounts')

def login_callback(request):
    if 'code' not in request.GET:
        raise PermissionDenied

    if 'state' not in request.GET:
        raise PermissionDenied

    if request.session.get('oauth_login_state') != request.GET['state']:
        raise PermissionDenied

    user = authenticate(code=request.GET['code'])

    if user is not None and user.is_active:
        auth_login(request, user)
        request.session['oauth_token'] = getattr(user, 'oauth_token', None)
        request.session['oauth_user_data'] = dict(synced_at=time())

        return redirect(request.session.get('next', settings.LOGIN_REDIRECT_URL))

    raise PermissionDenied
