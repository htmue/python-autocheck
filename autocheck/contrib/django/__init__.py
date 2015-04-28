# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-19.
#=============================================================================
#   __init__.py --- Django support
#=============================================================================
from __future__ import absolute_import, unicode_literals


django = None

try:
    import django
except ImportError:
    pass
else:
    try:
        from .discoveryrunner import TestSuiteRunner  # noqa
    except ImportError:
        try:
            from .testsuiterunner import TestSuiteRunner  # noqa
        except ImportError:
            pass

if django is not None:
    try:
        from south.management.commands import patch_for_test_db_setup
    except ImportError:
        pass
    else:
        patch_for_test_db_setup()

#.............................................................................
#   __init__.py
