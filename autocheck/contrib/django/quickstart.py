# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-19.
#=============================================================================
#   quickstart.py --- Quick test database setup
#=============================================================================
"""
Extremely fast Django test runner, based on the idea that your database schema
and fixtures are changed much more seldom that your code and tests.  All you
need is to make sure that your "quickstart.sqlite" database file is always up
to date.

BEWARE: Don't run this test runner on production server. It assumes that you
use only one database configured as "default", and its db engine is SQLite.
Otherwise your tests can eat your data!

How to use it:

1. Install sqlitebck:

    pip install sqlitebck

2. Create database alias named "quickstart" with sqlite3 backend in your
   settings.py:

    DATABASES = {
         ..
        'quickstart': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '.../quickstart.sqlite',
        },
    }

3. Create quickstart.sqlite:

     ./manage.py migrate --database quickstart

4. Redefine variable TEST_RUNNER in the settings.py:

    TEST_RUNNER = 'autocheck.contrib.django.TestSuiteRunner'

5. If your schema and has changed, apply migrations to quickstart.sqlite:

     ./manage.py migrate --database quickstart

Original code and docstring: https://gist.github.com/NetAngels/1044215

We use sqlitebck: https://pypi.python.org/pypi/sqlitebck instead of apsw.
"""
from __future__ import absolute_import, unicode_literals

from django.db import connections


try:
    import sqlitebck
except ImportError:
    sqlitebck = None


class QuickstartMixin(object):

    def setup_databases(self, **kwargs):
        if sqlitebck is not None and 'quickstart' in connections:
            quickstart = connections['quickstart']
            connection = connections['default']
            quickstart.ensure_connection()
            connection.ensure_connection()
            sqlitebck.copy(quickstart.connection, connection.connection)
            serialize = connection.settings_dict.get(
                "TEST", {}).get("SERIALIZE", True)
            if serialize:
                serialized = connection.creation.serialize_db_to_string()
                connection._test_serialized_contents = serialized
            return 'quickstart'
        else:
            return super(QuickstartMixin, self).setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        if old_config != 'quickstart':
            super(QuickstartMixin, self).teardown_databases(
                old_config, **kwargs)

#.............................................................................
#   quickstart.py
