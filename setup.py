# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   setup.py --- Install script
#=============================================================================
from distutils.core import setup


setup(
    name='autocheck',
    version='0.1.0',
    description='Improved unittest2 test runner',
    author='Hans-Thomas Mueller',
    author_email='htmue@mac.com',
    url='https://github.com/htmue/python-autocheck',
    packages=['autocheck'],
    scripts=['bin/autocheck'],
)

#.............................................................................
#   setup.py
