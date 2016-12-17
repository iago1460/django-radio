###
API
###

Api documentation.


*************
Browsable API
*************
*New in version 3.0*

RadioCo has a Web browsable API, go to http://127.0.0.1:8000/api/2/ in your browser to explore it.


Optionally these endpoints support filtering and ordering in the majority of the exposed fields.


Programmes
==========
Programmes can be filter using after and before parameters as well as Transmissions.

Example query to get all available programmes on New Year’s Eve order by name:

.. code-block:: bash

    http://127.0.0.1:8000/api/2/programmes?after=2016-12-31&before=2016-12-31&ordering=name


Transmissions
=============
Transmissions are always ordered by date, the after and before parameters are required.

Example query:

.. code-block:: bash

    http://127.0.0.1:8000/api/2/transmissions?after=2016-12-19&before=2016-12-26


Also is possible to request the dates in a specific timezone: 

.. code-block:: bash

    http://127.0.0.1:8000/api/2/transmissions?timezone=Europe%2FMadrid&after=2016-12-19&before=2016-12-26


Finally, there is a endpoint to get the current transmission:

.. code-block:: bash

    http://127.0.0.1:8000/api/2/transmissions/now

