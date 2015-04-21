autocheck
=========

Run Python unittests automatically. Re-run tests when source has changed.
Try to make intelligent decisions about which tests to run.


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

Install ```watchdog``` kernel support according to
https://pythonhosted.org/watchdog/installation.html.


Django support
--------------

Tell django to use our test runner, in ```settings```:

    TEST_RUNNER = 'autocheck.contrib.django.TestSuiteRunner'

Or on the command line:

    ./manage.py test --testrunner=autocheck.contrib.django.TestSuiteRunner

Run tests automatically whenever source has changed:

    $ autocheck

```autocheck``` tries to figure out if it runs in a django project
(```./manage.py``` exists, contains ```DJANGO_SETTINGS_MODULE```, ```django```
is importable). Additionally, if a file ```test_settings.py``` exists,
```DJANGO_SETTINGS_MODULE=test_settings``` is added to the environment.

Behind the scenes, there are two test runners for django, selected during
import of ```autocheck.contrib.django.TestSuiteRunner```:

- ```autocheck.contrib.django.discoveryrunner.TestSuiteRunner``` for recent versions of django (>=1.6)

- ```autocheck.contrib.django.testsuiterunner.TestSuiteRunner``` for older versions (<1.6)

The latter is not compatible with the old ```./manage.py test``` command,
instead it tries to reproduce the interface of ```python -m unittest```.

The other one is a thin wrapper around django's ```DiscoverRunner```, adding a
few command line switches for our custom ```TestRunner```.


Statistics
----------

Dump the test database with:

    $ autocheck --stats

Or:

    $ autocheck --stats-flat


Tests
-----

[![Build Status](https://travis-ci.org/htmue/python-autocheck.svg)](https://travis-ci.org/htmue/python-autocheck)

Install test requirements:

    $ pip install .
    $ pip install -r requirements/test.txt

For Python-2.6 additionaly:

    $ pip install -r requirements/python-2.6.txt

Run in project directory:

    $ PYTHONPATH=. ./bin/autocheck discover -v --once

Tested against Python-2.6, 2.7, 3.3, 3.4, PyPy 2 and 3.


TODO
----

* make ```autocheck.autorunner``` file pattern configurable
* config file(s)
* documentation for tags and tag expressions
* documentation for autocheck command line flags
* ```--help``` for autocheck command


License
-------

This is free and unencumbered software released into the public domain.

see [UNLICENSE](http://unlicense.org/)
