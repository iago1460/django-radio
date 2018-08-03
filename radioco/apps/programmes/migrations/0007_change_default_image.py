# -*- coding: utf-8 -*-


from django.db import migrations
from django.templatetags.static import static

def change_programmes(apps, schema_editor):
    # We can't import the Programme model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Programme = apps.get_model("programmes", "Programme")
    for programme in Programme.objects.all():
        print(programme.photo.name)
        if programme.photo.name == static('radio/images/default-programme-photo.jpg'):
            programme.photo = 'defaults/default-programme-photo.jpg'
            programme.save()


def change_users(apps, schema_editor):
    UserProfile = apps.get_model("users", "UserProfile")
    for profile in UserProfile.objects.all():
        if profile.avatar.name == static('radio/images/default-userprofile-avatar.jpg'):
            profile.avatar = 'defaults/default-userprofile-avatar.jpg'
            profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0006_auto_20160104_2029'),
        ('users', '0003_auto_20160104_2029'),
    ]

    operations = [
        migrations.RunPython(change_programmes),
        migrations.RunPython(change_users),
    ]
