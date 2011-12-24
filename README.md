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

    $ pip install -e git+https://github.com/htmue/python-autocheck#egg=autocheck

Optionally, for Growl support:

    $ pip install gntp

Install ```python-observer``` kernel support according to https://github.com/htmue/python-observer.


Tests
-----

Install test requirements:

    $ pip install -r requirements/test.txt

Run:

    $ autocheck discover -v --once


License
-------

This is free and unencumbered software released into the public domain.

see [UNLICENSE](http://unlicense.org/)
