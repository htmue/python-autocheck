# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   setup.py --- Install script
#=============================================================================
import sys

from setuptools import setup, find_packages


install_requires = ['PyYAML', 'watchdog', 'python-termstyle', 'six']

if sys.version_info[:2] == (2, 6):
    install_requires.extend(('argparse', 'unittest2'))

setup(
    name='autocheck',
    version='0.2.6',
    description='Improved unittest test runner',
    author='Hans-Thomas Mueller',
    author_email='htmue@mac.com',
    url='https://github.com/htmue/python-autocheck',
    packages=find_packages(),
    package_data=dict(
        autocheck=['*.yaml', 'colourschemes/*.yaml', 'images/*.png']),
    entry_points=dict(console_scripts=['autocheck = autocheck.main:main']),
    install_requires=install_requires,
    test_suite='vows',
    tests_require=['mock', 'should-dsl'],
)

#.............................................................................
#   setup.py
