import logging
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from oauth2_login_client.utils import oauth_session

class OAuthBackend(ModelBackend):

    def authenticate(self, code=None):
        oauth = oauth_session()
        token = oauth.fetch_token(
            settings.OAUTH_SERVER + settings.OAUTH_TOKEN_URL,
            code=code,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            verify=not settings.DEBUG,
        )

        r = oauth.get(settings.OAUTH_SERVER + settings.OAUTH_RESOURCE_URL)
        if r.status_code != 200:
            return None

        userdata = json.loads(r.content)
        if not userdata or 'email' not in userdata:
            return None

        primary = userdata['email']

        emails = [primary]
        if getattr(settings, 'OAUTH_UPDATE_EMAIL', False):
            emails += userdata.get('previous_emails', [])

        usermodel = get_user_model()

        for email in emails:
            try:
                user = usermodel.objects.get(email=email)
                if user.email != primary:
                    user.email = primary
                    user.save()
                return user
            except usermodel.DoesNotExist:
                pass
