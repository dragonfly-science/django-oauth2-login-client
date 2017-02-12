from django.conf.urls import url, include
from .views import login_redirect, account_redirect, login_callback

urlpatterns = [
    url(r'^login/callback', login_callback),
    url(r'^login', login_redirect),
    url(r'^account', account_redirect),
]
