# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-20.
#=============================================================================
#   testsuiterunner.py --- Django test suite runner
#=============================================================================
from django.test.simple import DjangoTestSuiteRunner

from .quickstart import QuickstartMixin
from autocheck.db import Database
from autocheck.testrunner import TestRunner, TestProgram


class TestSuiteRunner(QuickstartMixin, DjangoTestSuiteRunner):
    opts = dict(
        failfast = '--failfast',
        catch = '--catch',
        buffer = '--buffer',
        pattern = '-p',
        verbose = '-v',
    )
    discover_opts = dict(
        start = '-s',
        top_level = '-t',
    )
    discover_opts.update(opts)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        argv = ['./manage.py unittest']
        discover = len(test_labels) == 0 or len(test_labels) == 1 and test_labels[0] == 'discover'
        if discover:
            argv.append('discover')
            opts = self.discover_opts
        else:
            opts = self.opts
        for key, value in kwargs.items():
            if key in opts:
                option = opts[key]
                if value is True:
                    argv.append(option)
                elif value is not False and value is not None:
                    argv.append(option)
                    argv.append(value)
        if not discover:
            argv.extend(test_labels)
        self.setup_test_environment()
        old_config = self.setup_databases()
        result = TestProgram(module=None, argv=argv, testRunner=TestRunner, database=Database())
        self.teardown_databases(old_config)
        self.teardown_test_environment()
        return self.suite_result(suite, result)

#.............................................................................
#   testsuiterunner.py
