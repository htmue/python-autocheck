# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   testrunner.py --- Running tests
#=============================================================================
from __future__ import absolute_import, unicode_literals

import datetime
import logging
import sys
import time

from six.moves import map, zip

from . import status
from .colorizer import ColourWritelnDecorator, ColourScheme
from .compat import unittest
from .encoding import ConsoleBuffer, smart_str
from .filtersuite import filter_suite
from .tagexpression import TagExpression


try:
    from .growler import Notifier
except ImportError:
    growler = None
else:
    growler = Notifier()


def camel_to_underscore(value):
    def camel_to_underscore():
        yield value[0]
        for c, d in zip(value[1:], value[2:] + '_'):
            if c.isupper() and not (d == '_' or d.isupper()):
                yield '_'
                yield c.lower()
            else:
                yield c
    return ''.join(camel_to_underscore())


class LogHandler(logging.StreamHandler):

    def __init__(self):
        logging.Handler.__init__(self)

    @property
    def stream(self):
        return sys.stderr


class TestResult(unittest.TestResult):

    """A test result class that can print formatted text results to a stream.

    Used by TestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1,
                 colourscheme='light', database=None, now_function=None):
        super(TestResult, self).__init__()
        self.scheme = colourscheme if isinstance(
            colourscheme, ColourScheme) else ColourScheme(colourscheme)
        self.stream = stream if isinstance(
            stream, ColourWritelnDecorator) else ColourWritelnDecorator(stream)
        self.showAll = verbosity > 1
        self.specs = descriptions and self.showAll
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self.success_count = 0
        self.current_class = None
        self.database = database
        self.now = now_function or datetime.datetime.utcnow

    def getSpecDescription(self, test):  # noqa
        if self.specs:
            doc_first_line = test.shortDescription()
            if self.descriptions and doc_first_line:
                spec = doc_first_line
            else:
                spec = self._specify(test)
            if test.__class__ != self.current_class:
                self.current_class = test.__class__
                prefix = self._specify_class()
            else:
                prefix = '  '
            return prefix + spec
        else:
            return self.getDescription(test)

    def getDescription(self, test):  # noqa
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def startTestRun(self):  # noqa
        super(TestResult, self).startTestRun()
        self.results = []

    def stopTestRun(self):  # noqa
        super(TestResult, self).stopTestRun()
        if self.database is not None and self.results:
            self.database.add_results(self.results)

    def startTest(self, test):  # noqa
        super(TestResult, self).startTest(test)
        if self.showAll:
            self.stream.write(self.getSpecDescription(test))
            self.stream.write(' ... ')
            if self.specs and getattr(test, 'is_scenario', False):
                self.stream.writeln()
            self.stream.flush()
        self.time_started = self.now()

    def addSuccess(self, test):  # noqa
        super(TestResult, self).addSuccess(test)
        self._add_result(test, status.ok.key)
        self.success_count += 1
        self._write_scenario_result_indent(test)
        self._write_status(status.ok)

    def addError(self, test, err):  # noqa
        super(TestResult, self).addError(test, err)
        self._add_result(test, status.error.key)
        self._write_scenario_result_indent(test)
        self._write_status(status.error)

    def addFailure(self, test, err):  # noqa
        super(TestResult, self).addFailure(test, err)
        self._add_result(test, status.fail.key)
        self._write_scenario_result_indent(test)
        self._write_status(status.fail)

    def addSkip(self, test, reason):  # noqa
        super(TestResult, self).addSkip(test, reason)
        self._add_result(test, status.skip.key)
        colour = self.scheme.skip
        if self.showAll:
            self._write_scenario_result_indent(test)
            self._write('{0} {1!r}'.format(status.skip.name, reason),
                        None, colour=colour)
        elif self.dots:
            self._write(None, status.skip.key, colour=colour)

    def addExpectedFailure(self, test, err):  # noqa
        super(TestResult, self).addExpectedFailure(test, err)
        self._add_result(test, status.expected_failure.key)
        if self.showAll:
            self._write_scenario_result_indent(test)
        self._write_status(status.expected_failure)

    def addUnexpectedSuccess(self, test):  # noqa
        super(TestResult, self).addUnexpectedSuccess(test)
        self._add_result(test, status.unexpected_success.key)
        if self.showAll:
            self._write_scenario_result_indent(test)
        self._write_status(status.unexpected_success)

    def startStep(self, step):  # noqa
        if self.specs and self.showAll:
            self.stream.write('    %s ... ' % step)
            self.stream.flush()

    def stopStep(self, step):  # noqa
        if self.specs and self.showAll:
            self.stream.writeln()

    def addStepSuccess(self, step):  # noqa
        if self.specs and self.showAll:
            self.stream.write('ok', colour=self.scheme.ok)

    def addStepError(self, step):  # noqa
        if self.specs and self.showAll:
            self.stream.write('error', colour=self.scheme.error)

    def addStepFailure(self, step):  # noqa
        if self.specs and self.showAll:
            self.stream.write('fail', colour=self.scheme.fail)

    def addStepUndefined(self, step):  # noqa
        if self.specs and self.showAll:
            self.stream.write('undefined', colour=self.scheme.skip)

    def printErrors(self):  # noqa
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors, colour=self.scheme.error)
        self.printErrorList('FAIL', self.failures, colour=self.scheme.fail)

    def printErrorList(self, flavour, errors, colour):  # noqa
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(
                '%s: %s' % (flavour, self.getDescription(test)), colour=colour)
            self.stream.writeln(self.separator2)
            self.stream.writeln(smart_str(err), colour=colour)

    def _add_result(self, test, status):
        if self.database is not None:
            self.results.append((test, self.time_started, self.now(), status))

    def _specify(self, test):
        if test._testMethodName.startswith('test_'):
            return test._testMethodName[5:].replace('_', ' ')
        else:
            return str(test)

    def _specify_class(self):
        name = self.current_class.__name__
        if name.endswith('Test') or name.endswith('Vows'):
            name = name[:-4]
        return '\n%s:\n  ' % ' '.join(
            camel_to_underscore(name).replace('_', ' ').split())

    def _write(self, all, dots, colour):
        if self.showAll and all is not None:
            self.stream.writeln(all, colour=colour)
        elif self.dots and dots is not None:
            self.stream.write(dots, colour=colour)
            self.stream.flush()

    def _write_status(self, status):
        self._write(
            status.name, status.key, getattr(self.scheme, status.colour))

    def _write_scenario_result_indent(self, test):
        if self.specs and getattr(test, 'is_scenario', False):
            self.stream.write('  ... ')

    def _setupStdout(self):  # noqa
        if self.buffer:
            if self._stderr_buffer is None:
                self._stderr_buffer = ConsoleBuffer()
                self._stdout_buffer = ConsoleBuffer()
            sys.stdout = self._stdout_buffer
            sys.stderr = self._stderr_buffer


class TestRunner(object):

    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    resultclass = TestResult
    database = None

    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None,
                 colourscheme='light', growler=growler, database=None,
                 full_suite=True, now_function=None):
        self.stream = ColourWritelnDecorator(stream)
        self.scheme = ColourScheme(colourscheme)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.growler = growler
        if resultclass is not None:
            self.resultclass = resultclass
        if database is not None:
            self.database = database
        self.full_suite = full_suite
        self.now = now_function
        if self.now is None:
            self.now = datetime.datetime.utcnow

    def _makeResult(self):  # noqa
        return self.resultclass(self.stream, self.descriptions, self.verbosity,
                                self.scheme, self.database, self.now)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        unittest.registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        if self.database is not None:
            self.database.add_run()
        start_time = time.time()
        start_test_run = getattr(result, 'startTestRun', None)
        if start_test_run is not None:
            start_test_run()
        try:
            test(result)
        finally:
            stop_test_run = getattr(result, 'stopTestRun', None)
            if stop_test_run is not None:
                stop_test_run()
        stop_time = time.time()
        if self.database is not None:
            self.database.finish_run(self.full_suite)
        time_taken = stop_time - start_time
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln('Ran %d test%s in %.3fs' %
                            (run, run != 1 and 's' or '', time_taken))
        self.stream.writeln()

        expected_fails = unexpected_successes = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expected_fails, unexpected_successes, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write('FAILED', colour=self.scheme.FAIL)
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append((self.scheme.FAIL, 'failures: %d' % failed))
            if errored:
                infos.append((self.scheme.ERROR, 'errors: %d' % errored))
        else:
            failed = errored = None
            self.stream.write('OK', colour=self.scheme.OK)
        if skipped:
            infos.append((self.scheme.SKIP, 'skipped: %d' % skipped))
        if expected_fails:
            infos.append((
                self.scheme.EXPECTED_FAILURE,
                'expected failures: %d' % expected_fails))
        if unexpected_successes:
            infos.append((
                self.scheme.UNEXPECTED_SUCCESS,
                'unexpected successes: %d' % unexpected_successes))
        try:
            success = result.success_count
        except AttributeError:
            pass
        else:
            if not result.wasSuccessful():
                infos.append((self.scheme.OK, 'passed: %d' % success))
        if self.growler is not None:
            if errored:
                kind = 'error'
            elif failed:
                kind = 'fail'
            elif skipped or expected_fails:
                kind = 'pending'
            else:
                assert result.wasSuccessful()
                kind = 'pass'
            description = ['%d tests run' % run]
            if infos:
                description.append(
                    '(%s)' % ', '.join(info for _, info in infos))
            self.growler.notify(kind.title(), '\n'.join(description),
                                dict(error='fail').get(kind, kind))
        if infos:
            self.stream.writeln(
                ' (%s)' % (', '.join(c(info) for c, info in infos),))
        else:
            self.stream.writeln()
        return result


class TestProgram(unittest.TestProgram):

    def __init__(self, module='__main__', defaultTest=None, argv=None,  # noqa
                 testRunner=None, testLoader=unittest.defaultTestLoader,
                 exit=True, verbosity=1, failfast=None, catchbreak=None,
                 buffer=None, database=None):
        self.database = database
        self.run_tags = None

        super(TestProgram, self).__init__(
            module=module, defaultTest=defaultTest, argv=argv,
            testRunner=testRunner, testLoader=testLoader, exit=exit,
            verbosity=verbosity, failfast=failfast, catchbreak=catchbreak,
            buffer=buffer)

    def parseArgs(self, argv):  # noqa
        new_args = []
        i = 0
        while i < len(argv):
            arg = argv[i]
            if arg.startswith('--tags'):
                if self.run_tags is None:
                    self.run_tags = TagExpression()
                if arg.startswith('--tags='):
                    arg = arg[7:]
                else:
                    i += 1
                    arg = argv[i]
                self.run_tags.parse_and_add(arg)
            else:
                new_args.append(arg)
            i += 1
        super(TestProgram, self).parseArgs(new_args)

    def runTests(self):  # noqa
        if self.catchbreak:
            unittest.installHandler()
        if self.run_tags is not None:
            self.test = self.run_tags.filter_suite(self.test)
        tests_to_run, full_suite = filter_suite(self.test, self.database)
        test_runner = self.testRunner(
            verbosity=self.verbosity,
            failfast=self.failfast, buffer=self.buffer,
            database=self.database, full_suite=full_suite)
        self.result = test_runner.run(tests_to_run)
        if self.exit:
            sys.exit(not self.result.wasSuccessful())


if __name__ == '__main__':
    import sys
    if sys.argv[0].endswith('__main__.py'):
        sys.argv[0] = 'python -m autocheck.testrunner'

    from unittest.main import USAGE_AS_MAIN
    TestProgram.USAGE = USAGE_AS_MAIN

    TestProgram(module=None, testRunner=TestRunner)


__test__ = False

#.............................................................................
#   testrunner.py

# Derived from Python-2.7.1 unittest.runner, unittest.result, traceback
# Copyright © 2001-2010 Python Software Foundation; All Rights Reserved
# http://docs.python.org/license.html
