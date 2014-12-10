##########################
Installing web application
##########################

This tutorial is written for Python 2.7 and Ubuntu 12.04 or later.


********************
Installing on Ubuntu
********************

If you're using Ubuntu (tested with 14.04), the following should get you started:

.. code-block:: bash

    sudo apt-get install git-core python-dev python-pip python-virtualenv

Next, download the project and cd into it:

.. code-block:: bash

    git clone https://github.com/iago1460/radioco
    cd radioco

Create and switch to the virtualenv at the command line by typing:

.. code-block:: bash

    virtualenv .
    source bin/activate
  
Install the requirements:

.. code-block:: bash

    pip install -r requirements.txt

Setup the database:

.. code-block:: bash

    python manage.py migrate

Create a superuser:

.. code-block:: bash

    python manage.py createsuperuser
    
*******
Testing
*******

Let’s verify your installation

.. code-block:: bash

    python manage.py runserver

Now that the server’s running, visit http://127.0.0.1:8000/

.. warning::
    Don’t use this server in anything resembling a production environment. 

