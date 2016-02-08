#################
Production Setup
#################
The Internet is a hostile environment. Before deploying this project, you should take some time to 
review your settings, with security, performance, and operations in mind.

.. note::
    Please, review the `deployment checklist <https://docs.djangoproject.com/en/dev/howto/deployment/checklist/>`_,
    make sure to override at least the SECRET_KEY, take a look to the Reference/Application Setup section.


You have multiple options to deploy a Django application, we provide default out of the box configuration to make
this procedure a bit easier.

******
Heroku
******

RadioCo is already configured to easily deploy on Heroku, check out the folder ``radio/configs/heroku/`` and
make sure to override the default settings creating a ``local_settings.py`` file.
Navigate to the project root and then run::

    fab save_changes
    fab heroku_setup
    fab master heroku_deploy


**********************
Deployment with docker
**********************

`Docker <https://www.docker.com/>`_ is a containerization tool used for spinning up isolated, reproducible application 
environments. The stack includes a separate container for each service using Docker Compose.

Along with Docker we will be using Docker Compose. Check the `official documentation <https://docs.docker.com/engine/installation/>`_ to install docker.


Creating a custom image
=======================

Create a image with your current setup, navigate to the project root and then run::

    docker-compose build



Using the official image
========================

If you don't need/want customization you can use the `official RadioCo image <https://hub.docker.com/u/radioco/>`_ from Docker Hub,
download the repository `docker-radioco <https://github.com/iago1460/docker-radioco>`_ to get started.

.. warning::
    Make sure to change the default SECRET_KEY, the ``env`` file under the web folder contains the environment variables.
