# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-13.
#=============================================================================
#   __main__.py --- Test runner entry point
#=============================================================================
from __future__ import absolute_import, unicode_literals

import os.path
import sys

from .main import main


if sys.argv[0].endswith('__main__.py'):
    sys.argv[0:1] = [os.path.abspath(sys.executable), '-m', 'autocheck']

main()

#.............................................................................
#   __main__.py
