# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0007_change_default_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programme',
            name='language',
            field=models.CharField(default='es', max_length=7, verbose_name='language', choices=[('es', 'Spanish'), ('en', 'English'), ('gl', 'Galician')]),
        ),
    ]
