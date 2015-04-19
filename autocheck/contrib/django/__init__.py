# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-19.
#=============================================================================
#   __init__.py --- Django support
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

#.............................................................................
#   __init__.py
