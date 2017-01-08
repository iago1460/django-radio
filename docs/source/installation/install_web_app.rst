##########################
Installing web application
##########################

To allow RadioCo to generate correct dates it's necessary to set the timezone variable:

1. Find your timezone in `this list <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_
2. Go to the config folder (radioco/configs/base) and create if not exists a local_settings.py in the same directory than settings.py
3. Add to the local settings the variable timezone, for example: TIME_ZONE = "Europe/Madrid"


******************
Installing locally
******************

This tutorial is written for Python 2.7 and Ubuntu 12.04 or later.

Ubuntu
======

The easiest way of installing the app is using `Docker engine <https://docs.docker.com/engine/>`_, 
follow the `installation steps <https://docs.docker.com/engine/installation/>`_ to install Docker.


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


.. warning::

    If you have faced the error "ValueError: unknown locale: UTF-8" on MacOS X, execute:

    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8


Testing
-------

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

Locally
=======

RadioCo provides a staging environment, safer than the previous one but still insecure, **use at your own risk**.


.. code-block:: bash

    inv docker.setup -e staging


Now that the server’s running, visit http://127.0.0.1/


To create a superuser you still can use management commands:

.. code-block:: bash

    inv docker.manage -e staging -c "createsuperuser"


Openshift
=========
*New in version 3.1*

`OpenShift <https://www.openshift.com/>`_ is Red Hat's Platform-as-a-Service (PaaS) that allows developers to quickly develop, 
host, and scale applications in a cloud environment.

Prerequisites: An Openshift account

.. code-block:: bash

    inv --echo openshift.install_requirements
    inv --echo openshift.setup

    # And then every time that you wish to deploy:
    inv --echo openshift.deploy

.. note::

    If you are using a OS different than Ubuntu/Debian skip the install_requirements step and install manually
    `bower <https://bower.io/>`_  and `Openshift Client Tools <https://developers.openshift.com/managing-your-applications/client-tools.html>`_.

    Due to openshift old library versions Bower is required locally.
    The directive "--echo" will display shell commands as they are executed.


To create a superuser you can shell into the server using the following commands:

.. code-block:: bash

    inv openshift.ssh
    cd ${OPENSHIFT_REPO_DIR}
    python manage.py createsuperuser


Heroku
======
*Experimental in version 3.1*

Heroku is a platform as a service (PaaS) that enables developers to build, run, and operate applications 
entirely in the cloud

Prerequisites: A heroku account

.. code-block:: bash

    inv --echo heroku.install_requirements
    inv --echo heroku.setup

    # And then every time that you wish to deploy:
    inv --echo heroku.deploy

.. note::

    If you are using a OS different than Ubuntu/Debian skip the install_requirements command and
    install manually `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_.

.. warning::

    Uploaded images are not supported yet.
