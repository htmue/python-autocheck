# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-19.
#=============================================================================
#   discoveryrunner.py --- Django test suite runner
#=============================================================================
from django.test.runner import DiscoverRunner, reorder_suite

from .quickstart import QuickstartMixin
from autocheck.db import Database
from autocheck.tagexpression import TagExpression
from autocheck.testrunner import TestRunner


class TestSuiteRunner(QuickstartMixin, DiscoverRunner):
    test_runner = TestRunner
    
    def __init__(self, buffer=True, tags=[], **kwargs):
        super(TestSuiteRunner, self).__init__(**kwargs)
        self.buffer = buffer
        verbose = kwargs.pop('verbose', None)
        if verbose and self.verbosity < 2:
            self.verbosity = 2
        self.run_tags = None
        for tag in tags:
            if self.run_tags is None:
                self.run_tags = TagExpression()
            self.run_tags.parse_and_add(tag)

    @classmethod
    def add_arguments(cls, parser):
        super(TestSuiteRunner, cls).add_arguments(parser)
        parser.add_argument('--no-buffer', action='store_false', dest='buffer', default=True,
            help='Do not buffer stdout and stderr during test runs.')
        parser.add_argument('--no-verbose', action='store_false', dest='verbose', default=True,
            help='Do not run unittests verbose.')
        parser.add_argument('--tags', metavar='TAGEXPRESSION', action='append', default=[],
            help='Filter tests by tag expression.')

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        suite = super(TestSuiteRunner, self).build_suite(test_labels, extra_tests, **kwargs)
        if self.run_tags is not None:
            suite = self.run_tags.filter_suite(suite)
        return reorder_suite(suite, self.reorder_by, self.reverse)

    def run_suite(self, suite, **kwargs):
        resultclass = self.get_resultclass()
        return self.test_runner(
            buffer=self.buffer,
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=resultclass,
            database=Database(),
        ).run(suite)

#.............................................................................
#   discoveryrunner.py
