# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-29.
#=============================================================================
#   test_testrunner.py --- TestResult vows
#=============================================================================
from __future__ import absolute_import, unicode_literals

from functools import partial

import mock
import six
from should_dsl import should_not

from autocheck.compat import unittest
from autocheck.testrunner import TestRunner


if six.PY2:
    from StringIO import StringIO
else:
    from io import StringIO


@mock.patch('autocheck.db.Database')
class DatabaseTestRunnerVows(unittest.TestCase):

    class Test(unittest.TestCase):

        def runTest(self):
            pass

    def setUp(self):
        self.test = self.Test()
        self.stream = StringIO()

    def test_accepts_database_parameter(self, Database):
        db = Database()
        constructor = partial(TestRunner, database=db, stream=self.stream)

        constructor | should_not | throw(TypeError)

    def test_accepts_full_suite_parameter(self, Database):
        constructor = partial(TestRunner, full_suite=False, stream=self.stream)

        constructor | should_not | throw(TypeError)

    def test_passes_on_run_to_database(self, Database):
        db = Database()
        runner = TestRunner(database=db, stream=self.stream, growler=None)

        runner.run(self.test)

        db.add_run.assert_called_once_with()
        db.finish_run.assert_called_once_with(True)

    def test_passes_on_partial_run_to_database(self, Database):
        db = Database()
        runner = TestRunner(
            database=db, full_suite=False, stream=self.stream, growler=None)

        runner.run(self.test)

        db.add_run.assert_called_once_with()
        db.finish_run.assert_called_once_with(False)

    def test_accepts_now_function_parameter(self, Database):
        def now_function():
            pass
        constructor = partial(
            TestRunner, now_function=now_function, stream=self.stream)

        constructor | should_not | throw(TypeError)

#.............................................................................
#   test_testrunner.py
