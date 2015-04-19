autocheck
=========

Run Python unittests automatically. Re-run tests when source has changed. Try to make intelligent decisions about which tests to run.


Example
-------

In project directory with unittests:

    $ autocheck discover -v


Accepts the same options as ```python -m unittest```.


Installation
------------

    $ pip install autocheck

Optionally, for Growl support:

    $ pip install gntp

Install ```watchdog``` kernel support according to https://pythonhosted.org/watchdog/installation.html.


Django support
--------------

Add autocheck to installed apps:

    INSTALLED_APPS = (
        ...
        'autocheck.contrib.django',
        ...
    )

Run tests:

    $ autocheck


Tests
-----

Install test requirements:

    $ pip install -r requirements.txt
    $ pip install -r requirements/test.txt

For Python-2.6 additionaly:

    $ pip install -r requirements/python-2.6.txt

Run in project directory:

    $ PYTHONPATH=. ./bin/autocheck discover -v --once


TODO
----

* make ```autocheck.autorunner``` file pattern configurable


License
-------

This is free and unencumbered software released into the public domain.

see [UNLICENSE](http://unlicense.org/)
