# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   setup.py --- Install script
#=============================================================================
import sys

from distutils.core import setup


install_requires=[line.strip() for line in open('requirements.txt')]

if sys.version_info[:2] == (2, 6):
    install_requires.extend(line.strip() for line in open('requirements/python-2.6.txt'))

setup(
    name='autocheck',
    version='0.1.0',
    description='Improved unittest2 test runner',
    author='Hans-Thomas Mueller',
    author_email='htmue@mac.com',
    url='https://github.com/htmue/python-autocheck',
    packages=['autocheck'],
    package_data=dict(autocheck=['*.yaml', 'colourschemes/*.yaml']),
    scripts=['bin/autocheck'],
    install_requires=install_requires,
)

#.............................................................................
#   setup.py
