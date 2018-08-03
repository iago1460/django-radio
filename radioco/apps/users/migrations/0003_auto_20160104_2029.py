# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_change_textfield_to_richtextfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default='defaults/default-userprofile-avatar.jpg', upload_to='avatars/', verbose_name='avatar'),
        ),
    ]
