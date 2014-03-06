from django.conf import settings
from requests_oauthlib.oauth2_session import OAuth2Session

def oauth_session():
    return OAuth2Session(
        settings.OAUTH_CLIENT_ID,
        redirect_uri=settings.OAUTH_CALLBACK_URL
    )

def get_login_url():
    oauth = oauth_session()
    auth_url = settings.OAUTH_SERVER + settings.OAUTH_AUTHORIZATION_URL
    authorization_url, state = oauth.authorization_url(auth_url)
    return dict(
        authorization_url=authorization_url,
        state=state,
    )
