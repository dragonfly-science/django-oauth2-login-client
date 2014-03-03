import logging

from django.conf import settings
from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from oauth2_login_client.utils import get_login_url

def login_redirect(request):
    request.session['next'] = request.GET.get('next', request.path)
    return redirect(get_login_url())

def account_redirect(request):
    return redirect(settings.OAUTH_SERVER + '/accounts')

def login_callback(request):
    if 'code' not in request.GET:
        raise PermissionDenied

    user = authenticate(code=request.GET['code'])

    if user is not None and user.is_active:
        auth_login(request, user)
        return redirect(request.session.get('next', settings.LOGIN_REDIRECT_URL))

    raise PermissionDenied
