# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-19.
#=============================================================================
#   __inid__.py --- Django support
#=============================================================================
import os.path


try:
    from south.management.commands import patch_for_test_db_setup
except ImportError:
    pass
else:
    patch_for_test_db_setup()
try:
    from .discoveryrunner import TestSuiteRunner
except ImportError:
    from .testsuiterunner import TestSuiteRunner


def is_django():
    if os.path.exists('manage.py'):
        with open('manage.py') as manage:
            for line in manage:
                if 'DJANGO_SETTINGS_MODULE' in line:
                    try:
                        import django
                    except ImportError:
                        return
                    return True

#.............................................................................
#   discoveryrunner.py
