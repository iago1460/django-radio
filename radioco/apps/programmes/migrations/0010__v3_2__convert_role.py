# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django.conf import settings
from django.db import migrations, models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


LANGUAGE = settings.LANGUAGE_CODE

ROLES = dict((
    ('NO', "Not specified"),
    ('PR', "Presenter"),
    ('IN', "Informer"),
    ('CO', "Contributor")
))

# We need to keep a reference for the following translations
LEGACY_TRANSLATIONS = (
    _("Not specified"),
    _("Presenter"),
    _("Informer"),
    _("Contributor")
)


def convert_role_choice_to_value(apps, schema_editor):
    Participant = apps.get_model("programmes", "Participant")
    Role = apps.get_model("programmes", "Role")
    for obj in chain.from_iterable((Participant.objects.all(), Role.objects.all())):
        if obj.role:
            with translation.override(LANGUAGE):
                obj.role = translation.ugettext(ROLES[obj.role])
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0009__v3_0__small_tweaks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='role',
            field=models.CharField(max_length=60, null=True, verbose_name='role', blank=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.CharField(max_length=60, null=True, verbose_name='role', blank=True),
        ),
        migrations.RunPython(convert_role_choice_to_value),
    ]
