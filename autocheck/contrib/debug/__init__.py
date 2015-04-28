# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-11.
#=============================================================================
#   __init__.py ---
#=============================================================================
from __future__ import absolute_import, unicode_literals


try:
    from logging.config import dictConfig
except ImportError:
    pass
else:
    import os.path
    import yaml

    logging_yaml = os.path.join(os.path.dirname(__file__), 'logging.yaml')
    if os.path.isfile(logging_yaml):
        dictConfig(yaml.load(open(logging_yaml)))

#.............................................................................
#   __init__.py
