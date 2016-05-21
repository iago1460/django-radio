# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0002_change_language_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='summary',
            field=ckeditor.fields.RichTextField(verbose_name='summary', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='programme',
            name='language',
            field=models.CharField(default=b'af', max_length=7, verbose_name='language', choices=[(b'af', 'Afrikaans'), (b'ar', 'Arabic'), (b'ast', 'Asturian'), (b'az', 'Azerbaijani'), (b'bg', 'Bulgarian'), (b'be', 'Belarusian'), (b'bn', 'Bengali'), (b'br', 'Breton'), (b'bs', 'Bosnian'), (b'ca', 'Catalan'), (b'cs', 'Czech'), (b'cy', 'Welsh'), (b'da', 'Danish'), (b'de', 'German'), (b'el', 'Greek'), (b'en', 'English'), (b'en-au', 'Australian English'), (b'en-gb', 'British English'), (b'eo', 'Esperanto'), (b'es', 'Spanish'), (b'es-ar', 'Argentinian Spanish'), (b'es-mx', 'Mexican Spanish'), (b'es-ni', 'Nicaraguan Spanish'), (b'es-ve', 'Venezuelan Spanish'), (b'et', 'Estonian'), (b'eu', 'Basque'), (b'fa', 'Persian'), (b'fi', 'Finnish'), (b'fr', 'French'), (b'fy', 'Frisian'), (b'ga', 'Irish'), (b'gl', 'Galician'), (b'he', 'Hebrew'), (b'hi', 'Hindi'), (b'hr', 'Croatian'), (b'hu', 'Hungarian'), (b'ia', 'Interlingua'), (b'id', 'Indonesian'), (b'io', 'Ido'), (b'is', 'Icelandic'), (b'it', 'Italian'), (b'ja', 'Japanese'), (b'ka', 'Georgian'), (b'kk', 'Kazakh'), (b'km', 'Khmer'), (b'kn', 'Kannada'), (b'ko', 'Korean'), (b'lb', 'Luxembourgish'), (b'lt', 'Lithuanian'), (b'lv', 'Latvian'), (b'mk', 'Macedonian'), (b'ml', 'Malayalam'), (b'mn', 'Mongolian'), (b'mr', 'Marathi'), (b'my', 'Burmese'), (b'nb', 'Norwegian Bokmal'), (b'ne', 'Nepali'), (b'nl', 'Dutch'), (b'nn', 'Norwegian Nynorsk'), (b'os', 'Ossetic'), (b'pa', 'Punjabi'), (b'pl', 'Polish'), (b'pt', 'Portuguese'), (b'pt-br', 'Brazilian Portuguese'), (b'ro', 'Romanian'), (b'ru', 'Russian'), (b'sk', 'Slovak'), (b'sl', 'Slovenian'), (b'sq', 'Albanian'), (b'sr', 'Serbian'), (b'sr-latn', 'Serbian Latin'), (b'sv', 'Swedish'), (b'sw', 'Swahili'), (b'ta', 'Tamil'), (b'te', 'Telugu'), (b'th', 'Thai'), (b'tr', 'Turkish'), (b'tt', 'Tatar'), (b'udm', 'Udmurt'), (b'uk', 'Ukrainian'), (b'ur', 'Urdu'), (b'vi', 'Vietnamese'), (b'zh-cn', 'Simplified Chinese'), (b'zh-hans', 'Simplified Chinese'), (b'zh-hant', 'Traditional Chinese'), (b'zh-tw', 'Traditional Chinese')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='programme',
            name='synopsis',
            field=ckeditor.fields.RichTextField(verbose_name='synopsis', blank=True),
            preserve_default=True,
        ),
    ]
