from django.conf import settings
from django.contrib.auth import get_user_model
from requests_oauthlib.oauth2_session import OAuth2Session

from .models import RemoteUser


# back compatibility: use `OAUTH_TOKEN_URL` if `OAUTH_REFRESH_TOKEN_URL` not present
OAUTH_REFRESH_TOKEN_URL = getattr(settings, 'OAUTH_REFRESH_TOKEN_URL', settings.OAUTH_TOKEN_URL)


def oauth_session(
    token=None,
    client_id=settings.OAUTH_CLIENT_ID,
    redirect_uri=settings.OAUTH_CALLBACK_URL,
    auto_refresh_url=settings.OAUTH_SERVER + OAUTH_REFRESH_TOKEN_URL,
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


def create_user(userdata):
    """Create user with proper RemoteUser relationship

    :param userdata: user details
    :return: User, is_new
    """
    user_model = get_user_model()
    is_new = False

    try:
        user = user_model.objects.get(
            remoteuser__remote_username=userdata['username']
        )
    except user_model.DoesNotExist:
        # Create user
        max_len = user_model._meta.get_field("username").max_length

        new_username = userdata['username'][:max_len]
        i = 0
        while user_model.objects.filter(username=new_username).exists():
            if i > 1000:
                return None
            i += 1
            new_username = userdata['username'][:max_len - len(str(i))] + str(i)

        user = user_model.objects.create_user(
            username=new_username,
            email=userdata['email'],
            first_name=userdata['first_name'],
            last_name=userdata['last_name'],
        )
        user.save()

        user.remoteuser = RemoteUser(
            user=user, remote_username=userdata['username']
        )
        user.remoteuser.save()

        is_new = True

    return user, is_new
