## Oauth2 consumer for centralised django authentication

You have a bunch of django 1.5+ sites, which share some users in
common, and you would like your users to be able to manage their
passwords in a single place.

You also have a centralised oauth2 provider that you control, possibly
another django site using the oauth2_provider module from
[django-oauth-toolkit](https://github.com/evonove/django-oauth-toolkit).
Users are able to reset and change their passwords on that site.  All
your sites use SSL.

### Installation

    pip install git+https://github.com/dragonfly-science/django-oauth2-login-client.git

### In settings.py...

```python
...
AUTHENTICATION_BACKENDS = (
    'oauth2_login_client.backends.OAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)
...

# Provider
OAUTH_SERVER            = 'https://oauth2.provider.example.com'

# General urls on your provider:
OAUTH_AUTHORIZATION_URL = '/o/authorize'   # Authorization URL
OAUTH_TOKEN_URL         = '/o/token/'      # Access token URL

# The URL of some protected resource on your oauth2 server which you have configured to serve
# json-encoded user information (containing at least an email) for the user associated
# with a given access token.
OAUTH_RESOURCE_URL = '/userinfo'

# From the configuration of your client site in the oauth2 provider
OAUTH_CLIENT_ID         = 'gzUdompY9CtjguqXfgmZ;qM-Sg_JH=Pe2zZswUKo'
OAUTH_CLIENT_SECRET     = 'gMfBtGimi=NjdYvnLsU@!R@k4VEkruV1-Zkt.KEQ1Ead1Z;0OE?P:K2maN3seOCS..........'

# From 'oauth2_login_client.urls'
OAUTH_CALLBACK_URL      = 'https://consumer.site.example.com/oauth/login/callback'
...

# Optional permissions checking:
# Check permission based on a client site code passed in by the oauth2 server in the
# 'sites' element of the user info resource.
OAUTH_RESOURCE_CLIENT_CODE = 'clientcode'

# To periodically sync user details from auth server
# Add 'oauth2_login_client.middleware.OAuthMiddleware' to MIDDLEWARE_CLASSES
OAUTH_USER_SYNC_FREQUENCY = 3600 # seconds
```

### Login protected views

If you have `@login_required` views in on your site, it may be useful
to decorate these with your own custom decorator, and then put the
oauth2\_login\_client.views.login\_redirect function inside that
custom decorator, e.g. in decorators.py:

```python
from django.core.exceptions import PermissionDenied
from oauth2_login_client.views import login_redirect
from somewhere.else import my_user_has_permission
...
def my_custom_permission_check(view_function):
    def _view_function(request, *args, **kwargs):
        if not my_user_has_permission(request.user, **kwargs):
            if not user.is_authenticated():
                return login_redirect(request)
            raise PermissionDenied
        return view_function(request, *args, **kwargs)
    return _view_function
```

That way, logged-out users will automatically be bounced to the auth
server when trying to access a protected page on the client, and will
come back to the appropriate page after successful authentication.

### Todo:

If you have `@login_required` views in any 3rd party apps on your
site, it will be tricky to automatically redirect logged out users to
the authorization server when they hit those views.
