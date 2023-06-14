from django.conf.urls import include
from django.urls import re_path
from .views import login_redirect, account_redirect, login_callback

urlpatterns = [
    re_path(r'^login/callback', login_callback, name='oauth2_client_login_callback'),
    re_path(r'^login', login_redirect, name='oauth2_client_login_redirect'),
    re_path(r'^account', account_redirect, name='oauth2_client_account_redirect'),
]
