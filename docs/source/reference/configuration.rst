#############
Configuration
#############

RadioCo has a number of settings to configure its behaviour.


*****************
Application Setup
*****************
These settings should be available in your ``settings.py``.


USERNAME_RADIOCO_RECORDER
=========================

This specifies who is the user of the recorder program::

    USERNAME_RADIOCO_RECORDER = 'RadioCo_Recorder'

.. note::
    It's a good idea change this value for security reasons.


PROGRAMME_LANGUAGES
===================
*New in version 1.1*

Default: A tuple of all available languages.

This specifies which languages are available for language selection in your
programmes::

    gettext_noop = lambda s: s
    
    PROGRAMME_LANGUAGES = (
        ('es', gettext_noop('Spanish')),
        ('en', gettext_noop('English')),
    )

You can see the current list of translated languages by looking in django/conf/global_settings.py (or view the `online source <https://github.com/django/django/blob/master/django/conf/global_settings.py>`_).


**********************
Recorder Program Setup
**********************
The settings should be available in your `settings.ini <https://github.com/iago1460/django-radio-recorder/blob/master/recorder/settings.ini>`_.



*******************
Communication Setup
*******************

In your Admin interface go to **Podcast Configuration**, copy **Recorder token** and
put into the Recorder Program settings::

    token:8fdde6d703c05773084ea83e5ec2da62637666a0 #for example

Modify the **url** in your Recorder Program settings::

    url:http://yourdomain:80/api/1/
    
