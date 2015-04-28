# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-20.
#=============================================================================
#   testsuiterunner.py --- Django test suite runner
#=============================================================================
from __future__ import absolute_import, unicode_literals

from optparse import make_option

from django.test.simple import DjangoTestSuiteRunner

from ...db import Database
from ...testrunner import TestRunner, TestProgram
from .quickstart import QuickstartMixin


class TestSuiteRunner(QuickstartMixin, DjangoTestSuiteRunner):
    opts = dict(
        failfast='--failfast',
        catch='--catch',
        buffer='--buffer',
        pattern='-p',
        verbose='-v',
    )
    discover_opts = dict(
        start='-s',
        top_level='-t',
    )
    discover_opts.update(opts)
    option_list = (
        make_option(
            '--no-buffer', action='store_false', dest='buffer', default=True,
            help='Do not buffer stdout and stderr during test runs.'),
        make_option(
            '--no-verbose', action='store_false', dest='verbose', default=True,
            help='Do not run unittests verbose.'),
        make_option(
            '--tags', metavar='TAGEXPRESSION', action='append', default=[],
            help='Filter tests by tag expression.'),
        make_option(
            '-s', metavar='DIRECTORY', dest='start', default='.',
            help='Directory to start discovery (default: ".").'),
        make_option(
            '-p', metavar='PATTERN', dest='pattern',
            help='Pattern to match test files ("test*.py" default).'),
        make_option(
            '-t', metavar='DIRECTORY', dest='top_level', default='.',
            help='Top level directory of project (default: ".").'),
    )

    def __init__(self, **options):
        super(TestSuiteRunner, self).__init__(**options)
        self.options = options

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        argv = ['./manage.py unittest']
        discover = len(test_labels) == 0 or len(
            test_labels) == 1 and test_labels[0] == 'discover'
        opts = self.opts.copy()
        if discover:
            argv.append('discover')
            opts.update(self.discover_opts)
        for key, value in list(self.options.items()):
            if key in opts:
                option = opts[key]
                if value is True:
                    argv.append(option)
                elif value is not False and value is not None:
                    argv.append(option)
                    argv.append(value)
        for tag in self.options['tags']:
            argv.extend(('--tags', tag))
        if not discover:
            argv.extend(test_labels)
        self.setup_test_environment()
        old_config = self.setup_databases()
        result = TestProgram(
            module=None, argv=argv, testRunner=TestRunner, database=Database())
        self.teardown_databases(old_config)
        self.teardown_test_environment()
        return self.suite_result(None, result)

#.............................................................................
#   testsuiterunner.py
