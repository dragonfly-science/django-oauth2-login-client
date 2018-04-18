from django.conf.urls import url, include
from .views import login_redirect, account_redirect, login_callback

urlpatterns = [
    url(r'^login/callback', login_callback, name='oauth2_client_login_callback'),
    url(r'^login', login_redirect, name='oauth2_client_login_redirect'),
    url(r'^account', account_redirect, name='oauth2_client_account_redirect'),
]
