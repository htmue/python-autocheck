# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-29.
#=============================================================================
#   test_testrunner.py --- TestResult vows
#=============================================================================
from __future__ import unicode_literals

import datetime
import sys
from functools import partial
from io import StringIO

import mock
from should_dsl import should_not

from autocheck.compat import unittest
from autocheck.status import expected_failure, ok, error, fail, skip, unexpected_success
from autocheck.testrunner import TestResult, TestRunner


class TestTestCase(unittest.TestCase):
    
    class Test(unittest.TestCase):
        def runTest(self):
            pass
    
    def setUp(self):
        self.test = self.Test()
        self.stream = StringIO()


@mock.patch('autocheck.db.Database')
class DatabaseTestResultVows(TestTestCase):
    
    def test_accepts_database_parameter(self, Database):
        db = Database()
        constructor = partial(TestResult, database=db, stream=self.stream)
        
        constructor |should_not| throw(TypeError)
    
    def test_accepts_now_function_parameter(self, Database):
        def now_function():
            pass
        constructor = partial(TestResult, now_function=now_function, stream=self.stream)
        
        constructor |should_not| throw(TypeError)
    
    def start_test(self, db):
        start = datetime.datetime.utcnow()
        finish = start + datetime.timedelta(seconds=.1)
        now = mock.Mock('now', return_value=start)
        result = TestResult(database=db, stream=self.stream, now_function=now)
        result.startTestRun()
        result.startTest(self.test)
        now.return_value = finish
        return result, start, finish
    
    def stop_test(self, result):
        result.stopTest(self.test)
        result.stopTestRun()
    
    def test_passes_on_success_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)
        
        result.addSuccess(self.test)
        self.stop_test(result)
        
        db.add_results.assert_called_once_with([(self.test, start, finish, ok.key)])
    
    def test_passes_on_failure_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        try: x
        except Exception as e:
            result.addFailure(self.test, sys.exc_info())
        self.stop_test(result)

        db.add_results.assert_called_once_with([(self.test, start, finish, fail.key)])

    def test_passes_on_error_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        try: x
        except Exception as e:
            result.addError(self.test, sys.exc_info())
        self.stop_test(result)

        db.add_results.assert_called_once_with([(self.test, start, finish, error.key)])

    def test_passes_on_expected_failure_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)

        try: x
        except Exception as e:
            result.addExpectedFailure(self.test, sys.exc_info())
        self.stop_test(result)

        db.add_results.assert_called_once_with([(self.test, start, finish, expected_failure.key)])
    
    def test_passes_on_skip_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)
        
        result.addSkip(self.test, 'reason')
        self.stop_test(result)
        
        db.add_results.assert_called_once_with([(self.test, start, finish, skip.key)])
    
    def test_passes_on_unexpected_success_to_database(self, Database):
        db = Database()
        result, start, finish = self.start_test(db)
        
        result.addUnexpectedSuccess(self.test)
        self.stop_test(result)
        
        db.add_results.assert_called_once_with([(self.test, start, finish, unexpected_success.key)])


@mock.patch('autocheck.db.Database')
class DatabaseTestRunnerVows(TestTestCase):
    
    def test_accepts_database_parameter(self, Database):
        db = Database()
        constructor = partial(TestRunner, database=db, stream=self.stream)
        
        constructor |should_not| throw(TypeError)
    
    def test_accepts_full_suite_parameter(self, Database):
        db = Database()
        constructor = partial(TestRunner, full_suite=False, stream=self.stream)
        
        constructor |should_not| throw(TypeError)
    
    def test_passes_on_run_to_database(self, Database):
        db = Database()
        runner = TestRunner(database=db, stream=self.stream, growler=None)
        
        runner.run(self.test)
        
        db.add_run.assert_called_once_with()
        db.finish_run.assert_called_once_with(True)
    
    def test_passes_on_partial_run_to_database(self, Database):
        db = Database()
        runner = TestRunner(database=db, full_suite=False, stream=self.stream, growler=None)
        
        runner.run(self.test)
        
        db.add_run.assert_called_once_with()
        db.finish_run.assert_called_once_with(False)
    
    def test_accepts_now_function_parameter(self, Database):
        def now_function():
            pass
        constructor = partial(TestRunner, now_function=now_function, stream=self.stream)
        
        constructor |should_not| throw(TypeError)

#.............................................................................
#   test_testrunner.py
