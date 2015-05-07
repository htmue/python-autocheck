# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   setup.py --- Install script
#=============================================================================
from setuptools import setup, find_packages


with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='autocheck',
    version='0.2.7',
    description='Improved unittest test runner',
    long_description=long_description,
    author='Hans-Thomas Mueller',
    author_email='htmue@mac.com',
    url='https://github.com/htmue/python-autocheck',
    packages=find_packages(),
    package_data={
        'autocheck': ['*.yaml', 'colourschemes/*.yaml', 'images/*.png'],
    },
    entry_points={
        'console_scripts': ['autocheck = autocheck.main:main'],
    },
    install_requires=['PyYAML', 'watchdog', 'python-termstyle', 'six'],
    extras_require={
        ':python_version=="2.6"': ['unittest2'],
        'gntp': ['gntp>=0.7'],
    },
    test_suite='vows',
    tests_require=['mock', 'should-dsl'],
    license='UNLICENSE',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'License :: Public Domain',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
    ],
)

#.............................................................................
#   setup.py
