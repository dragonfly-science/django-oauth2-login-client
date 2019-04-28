import logging
import time
from django.conf import settings
from django.contrib.auth import logout

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from .utils import oauth_session, sync_user


class OAuthMiddleware(MiddlewareMixin):
    """If user details are stale, fetch and synchronise from the oauth server.
    If the user is no longer allowed to authenticate with the auth server, log
    them out."""

    def _sync_user(self, user, userdata):
        sync_user(user, userdata)

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        sync_frequency = getattr(settings, 'OAUTH_USER_SYNC_FREQUENCY', 3600)

        if not sync_frequency:
            return

        if 'oauth_token' not in request.session:
            return

        last_synced = request.session.get('oauth_user_data', {}).get('synced_at', 0)

        if time.time() - last_synced < sync_frequency:
            return

        token = request.session['oauth_token']
        oauth = oauth_session(token=token)
        r = oauth.get(settings.OAUTH_SERVER + settings.OAUTH_RESOURCE_URL,
                      verify=getattr(settings, 'OAUTH_VERIFY_SSL', True))

        if r.status_code == 403:
            logging.info("Forbidden by auth server")
            return logout(request)

        if r.status_code != 200:
            return

        if token != oauth.token:
            request.session['oauth_token'] = oauth.token

        userdata = r.json()

        if not userdata or 'username' not in userdata:
            return

        site_code = getattr(settings, 'OAUTH_RESOURCE_CLIENT_CODE', None)
        if site_code and site_code not in userdata.get('sites', []):
            logging.info("User not authorised for client site")
            return logout(request)

        if userdata['username'] != request.user.remoteuser.remote_username:
            logging.warn("Username mismatch")
            return logout(request)

        self._sync_user(request.user, userdata)
        request.session['oauth_user_data'] = dict(synced_at=time.time())
        return
