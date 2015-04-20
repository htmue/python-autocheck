# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-19.
#=============================================================================
#   __init__.py --- Django support
#=============================================================================
import os.path


try:
    from .discoveryrunner import TestSuiteRunner
except ImportError:
    try:
        from .testsuiterunner import TestSuiteRunner
    except ImportError:
        TestSuiteRunner = None

if TestSuiteRunner is None:
    def is_django():
        return False
else:
    try:
        from south.management.commands import patch_for_test_db_setup
    except ImportError:
        pass
    else:
        patch_for_test_db_setup()

    def is_django():
        if os.path.exists('manage.py'):
            with open('manage.py') as manage:
                for line in manage:
                    if 'DJANGO_SETTINGS_MODULE' in line:
                        return True

#.............................................................................
#   __init__.py
