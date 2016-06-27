import logging
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import RemoteUser
from .utils import oauth_session, sync_user

class OAuthBackend(ModelBackend):

    def authenticate(self, code=None):
        oauth = oauth_session()
        token = oauth.fetch_token(
            settings.OAUTH_SERVER + settings.OAUTH_TOKEN_URL,
            code=code,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            verify=getattr(settings, 'OAUTH_VERIFY_SSL', True),
        )

        r = oauth.get(settings.OAUTH_SERVER + settings.OAUTH_RESOURCE_URL)
        if r.status_code != 200:
            logging.warn("Error response from auth server")
            return None

        userdata = json.loads(r.content)

        if not userdata or 'email' not in userdata or 'username' not in userdata:
            logging.warn("Username and email not returned by auth server")
            return None

        site_code = getattr(settings, 'OAUTH_RESOURCE_CLIENT_CODE', None)
        if site_code and site_code not in userdata.get('sites', []):
            logging.info("User not authorised for client site")
            return None

        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(
                remoteuser__remote_username=userdata['username'])
        except usermodel.DoesNotExist:
            # Create user
            new_username = userdata['username'][:30]
            i = 0
            while usermodel.objects.filter(username=new_username).exists():
                if i > 1000:
                    return None
                i += 1
                new_username = userdata['username'][:30-len(str(i))] + str(i)
            user = usermodel.objects.create_user(
                username   = new_username,
                email      = userdata['email'],
                first_name = userdata['first_name'],
                last_name  = userdata['last_name'],
            )
            user.save()
            user.remoteuser = RemoteUser(
                user=user, remote_username = userdata['username'])
            user.remoteuser.save()

        sync_user(user, userdata)

        # Send the token back along with the user
        user.oauth_token = token

        return user
