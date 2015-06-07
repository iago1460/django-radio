############
django radio
############
.. image:: https://pypip.in/version/django-radio/badge.svg
    :target: https://pypi.python.org/pypi/django-radio/
.. image:: https://pypip.in/download/django-radio/badge.svg
    :target: https://pypi.python.org/pypi/django-radio/
.. image:: https://pypip.in/py_versions/django-radio/badge.svg
    :target: https://pypi.python.org/pypi/django-radio/
.. image:: https://pypip.in/license/django-radio/badge.svg
    :target: https://pypi.python.org/pypi/django-radio/


A radio management application that makes easy scheduling, live recording, publishing...

It is used by `RadioCo  <https://github.com/iago1460/radioco>`_.

********
Features
********

* designed to work with any web browser
* drag and drop scheduling calendar interface
* live shows can be recorded and published automatically
* complete authentication system (user accounts, groups, permissions)

* ...and much more

More information on `our website <http://radioco.org/>`_.

*************
Documentation
*************

Please head over to our `documentation <http://django-radio.readthedocs.org/>`_ for all
the details on how to install, extend and use django radio.

***********
Quick Start
***********
Open a terminal and introduce the following commands:

    git clone https://github.com/iago1460/django-radio
    cd django-radio
    virtualenv venv
    source venv/bin/activate
    pip install -r radio/configs/common/requirements.txt
    fab quickstart

Now that the server’s running (don't close the terminal), visit http://127.0.0.1:8000/

To access administrator site visit http://127.0.0.1:8000/admin/ using "admin/1234"

****************
Deploy on Heroku
****************
Quick deploy on Heroku:

    fab save_changes
    fab heroku_setup
    fab master heroku_deploy


