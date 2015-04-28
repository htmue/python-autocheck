# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-29.
#=============================================================================
#   compat.py --- Compatibility for Python 2.6
#=============================================================================
from __future__ import absolute_import, unicode_literals

import sys


if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest  # noqa
else:
    import unittest  # noqa

#.............................................................................
#   compat.py
