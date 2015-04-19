# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   setup.py --- Install script
#=============================================================================
import sys
import setuptools
from distutils.core import setup


install_requires=['PyYAML', 'watchdog', 'python-termstyle', 'six']

if sys.version_info[:2] == (2, 6):
    install_requires.append('unittest2')

setup(
    name='autocheck',
    version='0.2.2',
    description='Improved unittest test runner',
    author='Hans-Thomas Mueller',
    author_email='htmue@mac.com',
    url='https://github.com/htmue/python-autocheck',
    packages=['autocheck',
        'autocheck.contrib',
        'autocheck.contrib.django',
        'autocheck.contrib.django.management',
        'autocheck.contrib.django.management.commands',
    ],
    package_data=dict(autocheck=['*.yaml', 'colourschemes/*.yaml']),
    scripts=['bin/autocheck'],
    install_requires=install_requires,
)

#.............................................................................
#   setup.py
