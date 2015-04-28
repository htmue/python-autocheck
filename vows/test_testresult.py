# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-28.
#=============================================================================
#   test_testresult.py --- TestResult vows
#=============================================================================
from __future__ import absolute_import, unicode_literals

import datetime
import sys
from functools import partial

import mock
import six
from should_dsl import should_not

from autocheck.compat import unittest
from autocheck.status import (
    expected_failure, ok, error, fail, skip, unexpected_success
)
from autocheck.testrunner import TestResult


if six.PY2:
    from StringIO import StringIO
else:
    from io import StringIO


class TestResultTest(unittest.TestCase):
    stream_class = StringIO

    class Test(unittest.TestCase):

        def runTest(self):
            pass

    def setUp(self):
        self.test = self.Test()
        self.stream = self.stream_class()

    def start_test(self, db=None):
        start = datetime.datetime.utcnow()
        finish = start + datetime.timedelta(seconds=.1)
        now = mock.Mock('now', return_value=start)
        result = TestResult(database=db, stream=self.stream, now_function=now)
        result.buffer = True
        result.startTestRun()
        result.startTest(self.test)
        now.return_value = finish
        return result, start, finish

    def stop_test(self, result):
        result.stopTest(self.test)
        result.stopTestRun()


@mock.patch('autocheck.db.Database')
class DatabaseTestResultVows(TestResultTest):

    def test_accepts_database_parameter(self, Database):
        db = Database()
        constructor = partial(TestResult, database=db, stream=self.stream)

        constructor | should_not | throw(TypeError)

    def test_accepts_now_function_parameter(self, Database):
        def now_function():
            pass
        constructor = partial(
            TestResult, now_function=now_function, stream=self.stream)

        constructor | should_not | throw(TypeError)

    def test_passes_on_success_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        result.addSuccess(self.test)
        self.stop_test(result)

        db.add_results.assert_called_once_with(
            [(self.test, start, finish, ok.key)])

    def test_passes_on_failure_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        try:
            x
        except Exception:
            result.addFailure(self.test, sys.exc_info())
        self.stop_test(result)

        db.add_results.assert_called_once_with(
            [(self.test, start, finish, fail.key)])

    def test_passes_on_error_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        try:
            x
        except Exception:
            result.addError(self.test, sys.exc_info())
        self.stop_test(result)

        db.add_results.assert_called_once_with(
            [(self.test, start, finish, error.key)])

    def test_passes_on_expected_failure_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        try:
            x
        except Exception:
            result.addExpectedFailure(self.test, sys.exc_info())
        self.stop_test(result)

        db.add_results.assert_called_once_with(
            [(self.test, start, finish, expected_failure.key)])

    def test_passes_on_skip_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        result.addSkip(self.test, 'reason')
        self.stop_test(result)

        db.add_results.assert_called_once_with(
            [(self.test, start, finish, skip.key)])

    def test_passes_on_unexpected_success_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        result.addUnexpectedSuccess(self.test)
        self.stop_test(result)

        db.add_results.assert_called_once_with(
            [(self.test, start, finish, unexpected_success.key)])


class EncodingTestResultTest(TestResultTest):

    def test_can_handle_unicode_chars_in_exception(self):
        result, start, finish = self.start_test()
        try:
            raise Exception('1\xa0byte')
        except Exception:
            result.addError(self.test, sys.exc_info())
        self.stop_test(result)

        result.printErrors | should_not | throw(Exception)

    def test_can_handle_utf8_chars_in_exception(self):
        result, start, finish = self.start_test()
        try:
            raise Exception(b'1\xc2\xa0byte')
        except Exception:
            result.addError(self.test, sys.exc_info())
        self.stop_test(result)

        result.printErrors | should_not | throw(Exception)

    def test_can_handle_unicode_with_utf8_chars_in_exception(self):
        result, start, finish = self.start_test()
        try:
            raise Exception('1\xc2\xa0byte')
        except Exception:
            result.addError(self.test, sys.exc_info())
        self.stop_test(result)

        result.printErrors | should_not | throw(Exception)

#.............................................................................
#   test_testresult.py
