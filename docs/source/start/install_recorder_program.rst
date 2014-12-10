###########################
Installing recorder program
###########################

This tutorial is written for Python 2.7 and Ubuntu 12.04 or later.


********************
Installing on Ubuntu
********************

We’ll get started by setting up our environment.

.. code-block:: bash

    sudo apt-get install python-dev python-pip python-virtualenv git-core alsa-utils vorbis-tools


Next, download the project and create the virual environment:

.. code-block:: bash

    git clone https://github.com/iago1460/django-radio-recorder.git 
    cd django-radio-recorder


Create and activate a virtual env:

.. code-block:: bash

    virtualenv .
    source bin/activate

Install the requirements:

.. code-block:: bash

    pip install -r requirements.txt

Using your favorite text editor, configure the ``settings.ini`` file

Launch the program

.. code-block:: bash

    python main.py

