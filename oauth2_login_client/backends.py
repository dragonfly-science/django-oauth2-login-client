import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from .utils import oauth_session, sync_user, create_user


class OAuthBackend(ModelBackend):

    def _extract_userdata(self, response):
        return response.json()

    def _sync_user(self, user, userdata):
        sync_user(user, userdata)

    def _create_user(self, userdata):
        return create_user(userdata)

    def authenticate(self, request=None, code=None, redirect_uri=None):
        if redirect_uri is None:
            oauth = oauth_session()
        else:
            oauth = oauth_session(redirect_uri=redirect_uri)

        token = oauth.fetch_token(
            settings.OAUTH_SERVER + settings.OAUTH_TOKEN_URL,
            code=code,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            verify=getattr(settings, 'OAUTH_VERIFY_SSL', True),
        )

        r = oauth.get(settings.OAUTH_SERVER + settings.OAUTH_RESOURCE_URL)
        if r.status_code != 200:
            logging.warning("Error response from auth server")
            return None

        userdata = self._extract_userdata(r)

        if not userdata or 'email' not in userdata or 'username' not in userdata:
            logging.warning("Username and email not returned by auth server")
            return None

        site_code = getattr(settings, 'OAUTH_RESOURCE_CLIENT_CODE', None)
        if site_code and site_code not in userdata.get('sites', []):
            logging.info("User not authorised for client site")
            return None

        user, _ = self._create_user(userdata)
        self._sync_user(user, userdata)

        # Send the token back along with the user
        user.oauth_token = token

        return user
