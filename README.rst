#######
RadioCo
#######

.. image:: https://travis-ci.org/iago1460/django-radio.svg
   :target: https://travis-ci.org/iago1460/django-radio

.. image:: https://coveralls.io/repos/github/iago1460/django-radio/badge.svg?branch=master
   :target: https://coveralls.io/github/iago1460/django-radio?branch=master

.. image:: https://requires.io/github/iago1460/django-radio/requirements.svg?branch=master
   :target: https://requires.io/github/iago1460/django-radio/requirements/?branch=master
   :alt: Requirements Status

RadioCo is a radio management application that makes easy scheduling, live recording, publishing...

********
Features
********

* designed to work with any web browser
* drag and drop scheduling calendar interface
* live shows can be recorded and published automatically
* complete authentication system (user accounts, groups, permissions)

* ...and much more

.. image:: /screenshots/home_preview.png?raw=true

More information on `our website <http://radioco.org/>`_.

***********
Quick Start
***********

Install `Docker engine <https://docs.docker.com/engine/installation/>`_.

Open a terminal and introduce the following commands::

    pip install invoke==0.14.0
    git clone https://github.com/iago1460/django-radio
    cd django-radio
    inv quickstart


Now that the server’s running (don't close the terminal), visit http://127.0.0.1:8000/

To access administrator site visit http://127.0.0.1:8000/admin/ using "admin/1234"

*************
Documentation
*************

Please head over to our `documentation <http://django-radio.readthedocs.org/>`_ for all
the details on how to install, extend and use RadioCo.


Help us to translate
====================

We have a `Transifex account <https://www.transifex.com/projects/p/django-radio/>`_ where 
you can translate RadioCo.


*******
LICENSE
*******

Unless otherwise specified, all the project files are licensed under GNU General Public License.
The exceptions to this license are as follows:

* Bootstrap (http://getbootstrap.com):
    Licensed under MIT

* Jquery (https://jquery.com/):
    Licensed under MIT

* Query UI (https://jqueryui.com/):
    Licensed under MIT

* Font Awesome (http://fontawesome.io/):
	Licensed under SIL OFL 1.1

* FullCalendar (https://fullcalendar.io/license/):
    Licensed under MIT

* SOLID - Bootstrap 3 Theme (http://alvarez.is)
    Creative Commons Attribution 3.0 License
