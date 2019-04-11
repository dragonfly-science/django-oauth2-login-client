from django.conf import settings
from requests_oauthlib.oauth2_session import OAuth2Session


def oauth_session(
    token=None,
    client_id=settings.OAUTH_CLIENT_ID,
    redirect_uri=settings.OAUTH_CALLBACK_URL,
    auto_refresh_url=settings.OAUTH_SERVER + settings.OAUTH_TOKEN_URL,
    scope=getattr(settings, 'OAUTH_SCOPE', None),
    **kwargs
):

    return OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        auto_refresh_url=auto_refresh_url,
        token=token,
        scope=scope,
        **kwargs
    )


def get_login_url():
    oauth = oauth_session()
    auth_url = settings.OAUTH_SERVER + settings.OAUTH_AUTHORIZATION_URL
    authorization_url, state = oauth.authorization_url(auth_url, approval_prompt="auto")
    return dict(
        authorization_url=authorization_url,
        state=state,
    )

def sync_user(user, userdata):
    """Overwrite user details with data from the remote auth server"""

    for k in ['email', 'first_name', 'last_name']:
        if getattr(user, k) != userdata[k]:
            setattr(user, k, userdata[k])

    user.save()

    try:
        from allauth.account.models import EmailAddress
    except ImportError:
        return

    # Sync email address list
    for e in user.emailaddress_set.all():
        if e.email not in userdata['email_addresses']:
            e.delete()

    for e in userdata['email_addresses']:
        if user.emailaddress_set.filter(email=e).exists():
            continue
        emailaddress = EmailAddress(email=e, user=user)
        emailaddress.save()
