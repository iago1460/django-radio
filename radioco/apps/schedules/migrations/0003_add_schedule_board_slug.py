# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.template.defaultfilters import slugify


def migrate_board_slug(apps, schema_editor):
    ScheduleBoard = apps.get_model("schedules", "ScheduleBoard")
    for board in ScheduleBoard.objects.all():
        board.slug = slugify(board.name)
        board.save()


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002_migrate_to_rrules'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleboard',
            name='slug',
            field=models.SlugField(null=True, max_length=255),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_board_slug),
    ]
