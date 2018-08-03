# -*- coding: utf-8 -*-


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0010__v3_2__convert_role'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='participant',
            unique_together=set([('person', 'episode')]),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('person', 'programme')]),
        ),
    ]
