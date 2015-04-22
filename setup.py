# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   setup.py --- Install script
#=============================================================================
import sys
from distutils import spawn
from setuptools import setup


install_requires=['PyYAML', 'watchdog', 'python-termstyle', 'six']

if sys.version_info[:2] == (2, 6):
    install_requires.append('unittest2')

if spawn.find_executable('pandoc'):
    extra_setup = dict(
        setup_requires=['setuptools-markdown'],
        long_description_markdown_filename='README.md',        
    )
else:
    extra_setup = {}

setup(
    name='autocheck',
    version='0.2.6',
    description='Improved unittest test runner',
    author='Hans-Thomas Mueller',
    author_email='htmue@mac.com',
    url='https://github.com/htmue/python-autocheck',
    packages=['autocheck',
        'autocheck.contrib',
        'autocheck.contrib.django',
    ],
    package_data=dict(autocheck=['*.yaml', 'colourschemes/*.yaml', 'images/*.png']),
    scripts=['bin/autocheck'],
    install_requires=install_requires,
    **extra_setup
)

#.............................................................................
#   setup.py
