##########################
Installing web application
##########################

This tutorial is written for Python 2.7 and Ubuntu 12.04 or later.


********************
Installing on Ubuntu
********************

The easiest way of installing the app is using `Docker engine <https://docs.docker.com/engine/>`_

Follow the `installation steps <https://docs.docker.com/engine/installation/>`_

To allow RadioCo to generate correct dates it's necessary to set the timezone variable:

1. Find your timezone in `this list <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_
2. Go to the config folder (radioco/configs/base) and create if not exists a local_settings.py in the same directory than settings.py
3. Add to the local settings the variable timezone, for example: TIME_ZONE = "Europe/Madrid"


Open a terminal and introduce the following commands:

.. code-block:: bash

    sudo apt-get install git-core python-dev python-pip


Next, download the project and cd into it:

.. code-block:: bash

    git clone https://github.com/iago1460/django-radio
    cd django-radio


Install the python invoke library:

.. code-block:: bash

    pip install invoke==0.14.0


Execute the next command to deploy the app in docker, this step take some time:

.. code-block:: bash

    inv quickstart


Testing
=======

Let’s verify your installation

Now that the server’s running, visit http://127.0.0.1:8000/

.. warning::
    Don’t use this server in anything resembling a production environment. 



***************************
Using RadioCo on production
***************************

The Internet is a hostile environment.
Before deploying this project, you should take some time to review your settings, with security, performance, and operations in mind.
Keep in mind `this critical settings <https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/#critical-settings>`_.

RadioCo provides a staging environment, safer than the previous one but still insecure, **use at your own risk**.


.. code-block:: bash

    inv docker.build -e staging docker.run -e staging docker.setup -e staging

.. note::

    If you see an error related with postgress sql just run the command again


Now that the server’s running, visit http://127.0.0.1/


To create a superuser you still can use management commands:

.. code-block:: bash

    inv docker.manage -e staging -c "createsuperuser"