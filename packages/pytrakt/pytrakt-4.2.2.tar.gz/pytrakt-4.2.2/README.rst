PyTrakt
=======

.. image:: https://github.com/glensc/python-pytrakt/actions/workflows/test.yml/badge.svg
    :target: https://github.com/glensc/python-pytrakt/actions
    :alt: CI Status

.. image:: https://img.shields.io/pypi/dm/pytrakt.svg
    :target: https://pypi.org/project/pytrakt/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/l/pytrakt.svg
    :target: https://pypi.org/project/pytrakt/
    :alt: License

This module is designed to be a Pythonic interface to the `Trakt.tv <http://trakt.tv>`_.
REST API. The official documentation for which can be found `here <http://docs.trakt.apiary.io/#>`_.
trakt contains interfaces to all of the Trakt.tv functionality in an, ideally, easily
scriptable fashion. For more information on this module's contents and example usages
please see the `PyTrakt docs <https://glensc.github.io/python-pytrakt/>`_.

More information about getting started and accessing the information you thirst for
can be found throughout the documentation below.


Installation
------------
There are two ways through which you can install trakt

Install Via Pip
^^^^^^^^^^^^^^^
To install with `pip <http://www.pip-installer.org/>`_, just run this in your terminal::

    $ pip install pytrakt

Get the code
^^^^^^^^^^^^
trakt is available on `GitHub <https://github.com/glensc/python-pytrakt>`_.

You can either clone the public repository::

    $ git clone git://github.com/glensc/python-pytrakt.git

Download the `tarball <https://github.com/glensc/python-pytrakt/tarball/main>`_::

    $ curl -OL https://github.com/glensc/python-pytrakt/tarball/main

Or, download the `zipball <https://github.com/glensc/python-pytrakt/zipball/main>`_::

    $ curl -OL https://github.com/glensc/python-pytrakt/zipball/main

Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ python setup.py install

Contributing
------------
Pull requests are graciously accepted. Any pull request should not break any tests
and should pass `flake8` style checks (unless otherwise warranted). Additionally
the user opening the Pull Request should ensure that their username and a link to
their GitHub page appears in `CONTRIBUTORS.md <https://github.com/glensc/python-pytrakt/blob/main/CONTRIBUTORS.md>`_.


TODO
----
The following lists define the known functionality provided by the Trakt.tv API
which this module does not yet have support for. The current plan is that
support for the following features will be added over time. As always, if you
would like a feature added sooner rather than later, pull requests are most
definitely appreciated.

High Level API Features
^^^^^^^^^^^^^^^^^^^^^^^
- Pagination

Sync
^^^^
- Create a comment class to facilitate
  - returning an instance when a comment is created, instead of None
  - add ability to update and delete comments

Movies
^^^^^^
- movies/popular
- movies/played/{time_period}
- movies/watched/{time_period}
- movies/collected/{time_period}
- movies/anticipated
- movies/boxoffice
- movies/{slug}/stats

Shows
^^^^^
- Played
- Watched
- Collected
- Anticipated
- Collection Progress
- Watched Progress
- Stats

Seasons
^^^^^^^
- extended
  - images
  - episodes
  - full
- stats

Episodes
^^^^^^^^
- stats

Users
^^^^^
- hidden everything
- likes
  - comments
- comments
- UserList
  - comments
- history
- watchlists
  - seasons
  - episodes
