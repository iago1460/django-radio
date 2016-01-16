#################
Application Setup
#################
RadioCo can be adapted to your needs, you have three ways, in the administration page in the Global Settings section,
overriding the settings.py and overriding templates.


***************
Global settings
***************

Go to the admin section on your browser and edit the information available. You can setup the google analytics id here.


*********
Templates
*********

There is a empty folder called templates inside radio folder. You should override templates here, make sure to keep
the relative path.

For example, to override the episode detail page copy the episode_detail.html file from
radio/apps/programmes/templates/programmes/episode_detail.html to radio/templates/episode_detail.html


***********
Settings.py
***********

These settings are available in ``settings.py``. Your settings should be in a ``local_settings.py`` file in
the same directory as ``settings.py``.

.. warning::
    Your changes on settings should be in ``local_settings.py`` to avoid conflicts when update, create that file if
    it's necessary. Be aware that this file is excluded from Git.


USERNAME_RADIOCO_RECORDER
=========================

This specifies who is the user of the recorder program::

    USERNAME_RADIOCO_RECORDER = 'RadioCo_Recorder'

.. note::
    It's a good idea change this value for security reasons.


PROGRAMME_LANGUAGES
===================
*New in version 1.1*

Default: A tuple of the following three languages.

This specifies which languages are available for language selection in your
programmes::

    gettext_noop = lambda s: s
    
    PROGRAMME_LANGUAGES = (
        ('es', gettext_noop('Spanish')),
        ('en', gettext_noop('English')),
        ('gl', gettext_noop('Galician')),
    )

You can see the current list of translated languages by looking in django/conf/global_settings.py (or view the `online source <https://github.com/django/django/blob/master/django/conf/global_settings.py>`_).


Disqus
===================
*New in version 2.0*

Default: Disabled by default.

Add comments to your site with Disqus. `Create your account <https://disqus.com/admin/signup/>`_ and get `your API key <http://disqus.com/api/applications/>`_.::


    DISQUS_ENABLE = True
    DISQUS_API_KEY = 'YOUR_API_KEY'
    DISQUS_WEBSITE_SHORTNAME = 'YOUR_SHORTNAME'

