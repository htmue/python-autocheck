# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-19.
#=============================================================================
#   discoveryrunner.py --- Django test suite runner
#=============================================================================
from __future__ import absolute_import, unicode_literals

from django.test.runner import DiscoverRunner, reorder_suite

from ...db import Database
from ...filtersuite import filter_suite
from ...tagexpression import TagExpression
from ...testrunner import TestRunner
from .quickstart import QuickstartMixin


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
        self.database = Database()

    @classmethod
    def add_arguments(cls, parser):
        super(TestSuiteRunner, cls).add_arguments(parser)
        parser.add_argument(
            '--no-buffer', action='store_false', dest='buffer', default=True,
            help='Do not buffer stdout and stderr during test runs.')
        parser.add_argument(
            '--no-verbose', action='store_false', dest='verbose', default=True,
            help='Do not run unittests verbose.')
        parser.add_argument(
            '--tags', metavar='TAGEXPRESSION', action='append', default=[],
            help='Filter tests by tag expression.')

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        suite = super(TestSuiteRunner, self).build_suite(
            test_labels, extra_tests, **kwargs)
        if self.run_tags is not None:
            suite = self.run_tags.filter_suite(suite)
        suite, self.full_suite = filter_suite(suite, self.database)
        return reorder_suite(suite, self.reorder_by, self.reverse)

    def run_suite(self, suite, **kwargs):
        resultclass = self.get_resultclass()
        result = self.test_runner(
            buffer=self.buffer,
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=resultclass,
            database=self.database,
            full_suite=self.full_suite,
        ).run(suite)
        self.database.close()
        return result

#.............................................................................
#   discoveryrunner.py
