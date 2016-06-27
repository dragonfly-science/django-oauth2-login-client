from django.conf.urls import patterns
from .views import login_redirect, account_redirect, login_callback

urlpatterns = patterns('',
    (r'^login/callback', login_callback),
    (r'^login', login_redirect),
    (r'^account', account_redirect),
)
