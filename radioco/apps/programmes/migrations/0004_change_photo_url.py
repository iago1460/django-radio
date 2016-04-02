# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.templatetags.static import static

def change_photo_url(apps, schema_editor):
    # We can't import the Programme model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Programme = apps.get_model("programmes", "Programme")
    for programme in Programme.objects.all():
        if programme.photo.name == '/static/radio/images/default-programme-photo.jpg':
            programme.photo = static('radio/images/default-programme-photo.jpg')
            programme.save()

'''
# Can't use: 
# LookupError: No installed app with label 'users'.

def change_avatar_url(apps, schema_editor):
    UserProfile = radioco.apps.get_model("users", "UserProfile")
    for user in UserProfile.objects.all():
        if user.avatar.name == '/static/radio/images/default-userprofile-avatar.jpg':
            user.avatar = static('radio/images/default-userprofile-avatar.jpg')
            user.save()
'''

class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0003_change_textfield_to_richtextfield'),
    ]

    operations = [
        migrations.RunPython(change_photo_url),
        # migrations.RunPython(change_avatar_url),
    ]
