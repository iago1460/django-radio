# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0005_auto_20150531_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programme',
            name='photo',
            field=models.ImageField(default='defaults/default-programme-photo.jpg', upload_to='photos/', verbose_name='photo'),
        ),
    ]
