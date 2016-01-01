#######################
Development & community
#######################

RadioCo is an open-source project, and relies on its community of users to
keep getting better.

You don't need to be an expert developer to make a valuable contribution - all
you need is a little knowledge of the system, and a willingness to follow the
contribution guidelines.

Remember that contributions to the documentation are highly prized, and key to
the success of the project. Any time and effort you are willing to contribute is greatly appreciated!

*************
Branch policy
*************

* **master**: this is the current stable release, the version released on PyPI.
* **develop**: this branch always reflects a state with the latest delivered
  development changes for the next release.
* **feature branches**: these are used to develop new features.


************************
Contributing Translation
************************

For translators we have a `Transifex account
<https://www.transifex.com/projects/p/django-radio/>`_ where you can translate
the .po files and don't need to install git to be able to contribute. All
changes there will be automatically sent to the project.


**************************
Contributing Documentation
**************************

Perhaps considered "boring" by hard-core coders, documentation is sometimes even
more important than code! This is what brings fresh blood to a project, and
serves as a reference for old timers. On top of this, documentation is the one
area where less technical people can help most - you just need to write
semi-decent English. People need to understand you. We don't care about style or
correctness.

Documentation should be:

- written using valid `Sphinx`_/`restructuredText`_ syntax (see below for
  specifics) and the file extension should be ``.rst``
- written in English (we have standardised on British spellings)
- accessible - you should assume the reader to be moderately familiar with
  Python and Django, but not anything else. Link to documentation of libraries
  you use, for example, even if they are "obvious" to you

Merging documentation is pretty fast and painless.

Except for the tiniest of change, we recommend that you test them before
submitting.

Documentation markup
====================

Sections
--------

We use Python documentation conventions for section marking:

* ``#`` with overline, for parts
* ``*`` with overline, for chapters
* ``=``, for sections
* ``-``, for subsections
* ``^``, for subsubsections
* ``"``, for paragraphs

Inline markup
-------------

* use backticks - ````settings.py```` - for:
    * literals
    * filenames
    * names of fields and other items in the Admin interface:
* use emphasis - ``*Home*`` around:
    * the names of available options in the Admin
    * values in or of fields

References
----------

Use absolute links to other documentation pages - ``:doc:`/how_to/toolbar``` -
rather than relative links - ``:doc:`/../toolbar```. This makes it easier to
run search-and-replaces when items are moved in the structure.



.. _restructuredText: http://docutils.sourceforge.net/docs/ref/rst/introduction.html
.. _Sphinx: http://sphinx.pocoo.org/

