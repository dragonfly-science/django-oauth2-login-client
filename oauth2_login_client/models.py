from django.conf import settings
from django.db import models

class RemoteUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, help_text="Django user",
        primary_key=True, on_delete=models.CASCADE)
    remote_username = models.CharField(max_length=150, unique=True)
