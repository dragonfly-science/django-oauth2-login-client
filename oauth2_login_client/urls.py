from django.conf.urls import patterns
from oauth2_login_client.views import *

urlpatterns = patterns('',
    (r'^login/callback', login_callback),
    (r'^login', login_redirect),
    (r'^account', account_redirect),
)
