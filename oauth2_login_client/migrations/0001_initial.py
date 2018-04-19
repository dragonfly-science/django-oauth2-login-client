# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

def forwards_func(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    usermodel = apps.get_model(app_label, model_name)
    RemoteUser = apps.get_model("oauth2_login_client", "remoteuser")
    remote_users = []
    for u in usermodel.objects.filter(is_active=True):
        remote_users.append(RemoteUser(user=u, remote_username=u.username))
    RemoteUser.objects.bulk_create(remote_users)

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteUser',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, help_text=b'Django user', on_delete=models.CASCADE)),
                ('remote_username', models.CharField(unique=True, max_length=30)),
            ],
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
