# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-30.
#=============================================================================
#   test_filtersuite.py --- FilterSuite vows
#=============================================================================
from __future__ import absolute_import, unicode_literals

import os.path
import re
from functools import partial

import mock
import six
import yaml
from should_dsl import should
from six.moves import map

from autocheck.compat import unittest
from autocheck.filtersuite import filter_suite, flatten_suite


class FilterSuiteTestCase(unittest.TestCase):
    with open(os.path.splitext(__file__)[0] + '.yaml') as f:
        __suites = yaml.load(f)['suites']
    __cache = dict()

    class Test(unittest.TestCase):

        def runTest(self):
            pass

        @classmethod
        def add_test(cls, name):
            setattr(cls, 'test_' + name, cls.runTest)

    def get_suite(self, name):
        try:
            suite = self.__cache[name]
        except KeyError:
            suite = self.__cache[name] = self.add_suite(
                name, self.__suites[name])
        return suite

    def add_suite(self, name, defs):
        if not defs:
            return unittest.TestSuite()
        elif isinstance(defs, list):
            return self.add_tests(name, defs)
        elif isinstance(defs, dict):
            return self.add_suites(name, defs)
        else:
            raise RuntimeError('invalid suite definition: %s' % defs)

    def add_suites(self, name, defs):
        return unittest.TestSuite(
            self.add_suite('_'.join((name, key)), value)
            for key, value in sorted(defs.items())
        )

    def add_tests(self, name, defs):
        class Test(self.Test):
            pass
        Test.__name__ = str('Test_' + name)
        for test_name in defs:
            Test.add_test(test_name)
        return unittest.defaultTestLoader.loadTestsFromTestCase(Test)


class FilterSuiteTestCaseVows(FilterSuiteTestCase):

    def test_returns_TestSuite_instance(self):
        suite = self.get_suite('empty')

        suite |should| be_instance_of(unittest.TestSuite)

    def test_creates_empty_suite_properly(self):
        suite = self.get_suite('empty')

        map(str, suite) |should| each_be_equal_to([])

    def test_creates_flat_suite_properly(self):
        suite = self.get_suite('flat')

        map(suite_str, suite) |should| each_be_equal_to([
            'test_one (Test_flat)',
            'test_three (Test_flat)',
            'test_two (Test_flat)',
        ])

    def test_creates_nested_suite_properly(self):
        suite = self.get_suite('nested')

        map(suite_str, suite) |should| each_be_equal_to([
            '<TestSuite tests=['
                '<Test_nested_first testMethod=test_one>, '
                '<Test_nested_first testMethod=test_two>]>',
            '<TestSuite tests=['
                '<Test_nested_second testMethod=test_four>, '
                '<Test_nested_second testMethod=test_three>]>',
        ])  # noqa

    def test_creates_mixed_suite_properly(self):
        suite = self.get_suite('mixed')

        map(suite_str, suite) |should| each_be_equal_to([
            '<TestSuite tests=['
                '<Test_mixed_flat testMethod=test_one>, '
                '<Test_mixed_flat testMethod=test_two>]>',
            '<TestSuite tests=['
                '<TestSuite tests=['
                    '<Test_mixed_nested_first testMethod=test_four>, '
                    '<Test_mixed_nested_first testMethod=test_three>]>, '
                '<TestSuite tests=['
                    '<Test_mixed_nested_second testMethod=test_five>, '
                    '<Test_mixed_nested_second testMethod=test_six>]>, '
                    '<TestSuite tests=['
                        '<TestSuite tests=['
                            '<Test_mixed_nested_third_deep testMethod=test_eight>, '       # noqa
                            '<Test_mixed_nested_third_deep testMethod=test_seven>]>]>]>',  # noqa
        ])  # noqa


class FlattenSuiteVows(FilterSuiteTestCase):

    def test_returns_TestSuite_instance(self):
        suite = self.get_suite('empty')

        flattened = flatten_suite(suite)

        flattened |should| be_instance_of(unittest.TestSuite)

    def test_handles_empty_suite_properly(self):
        suite = self.get_suite('empty')

        flattened = flatten_suite(suite)

        next = partial(six.next, iter(flattened))
        next |should| throw(StopIteration)

    def test_handles_flat_suite_properly(self):
        suite = self.get_suite('flat')

        flattened = flatten_suite(suite)

        map(suite_str, flattened) |should| each_be_equal_to([
            'test_one (Test_flat)',
            'test_three (Test_flat)',
            'test_two (Test_flat)',
        ])

    def test_flattens_nested_suite_properly(self):
        suite = self.get_suite('nested')

        flattened = flatten_suite(suite)

        map(suite_str, flattened) |should| each_be_equal_to([
            'test_one (Test_nested_first)',
            'test_two (Test_nested_first)',
            'test_four (Test_nested_second)',
            'test_three (Test_nested_second)',
        ])

    def test_flattens_mixed_suite_properly(self):
        suite = self.get_suite('mixed')

        flattened = flatten_suite(suite)

        map(suite_str, flattened) |should| each_be_equal_to([
            'test_one (Test_mixed_flat)',
            'test_two (Test_mixed_flat)',
            'test_four (Test_mixed_nested_first)',
            'test_three (Test_mixed_nested_first)',
            'test_five (Test_mixed_nested_second)',
            'test_six (Test_mixed_nested_second)',
            'test_eight (Test_mixed_nested_third_deep)',
            'test_seven (Test_mixed_nested_third_deep)',
        ])


@mock.patch('autocheck.db.Database')
class FilterSuiteVows(FilterSuiteTestCase):

    def test_returns_TestSuite_instance(self, Database):
        suite = self.get_suite('flat')
        candidates = list(map(str, suite))[:1]
        db = Database()
        db.candidates = mock.Mock('candidates', return_value=set(candidates))

        filtered, full_suite = filter_suite(suite, db)

        filtered |should| be_instance_of(unittest.TestSuite)

    def test_returns_all_tests_when_there_is_no_database(self, Database):
        suite = self.get_suite('flat')

        filtered, full_suite = filter_suite(suite, None)

        full_suite |should| be(True)
        map(str, filtered) |should| each_be_equal_to(map(str, suite))

    def test_returns_all_tests_when_candidates_empty(self, Database):
        suite = self.get_suite('flat')
        db = Database()
        db.candidates = mock.Mock('candidates', return_value=set())

        filtered, full_suite = filter_suite(suite, db)

        full_suite |should| be(True)
        map(str, filtered) |should| each_be_equal_to(map(str, suite))

    def test_returns_only_tests_that_are_candidates_if_there_are_candidates(self, Database):  # noqa
        suite = self.get_suite('flat')
        candidates = ['test_two (%s.Test_flat)' % __name__]
        db = Database()
        db.candidates = mock.Mock('candidates', return_value=set(candidates))

        filtered, full_suite = filter_suite(suite, db)

        full_suite |should| be(False)
        map(str, filtered) |should| each_be_equal_to(candidates)

    def test_returns_all_tests_when_filtered_empty(self, Database):
        suite = self.get_suite('flat')
        candidates = ['unknown']
        db = Database()
        db.candidates = mock.Mock('candidates', return_value=set(candidates))

        filtered, full_suite = filter_suite(suite, db)

        full_suite |should| be(True)
        map(str, filtered) |should| each_be_equal_to(map(str, suite))


def suite_str(suite):
    return re.sub(
        r'unittest2?\.suite\.', '', str(suite)).replace(__name__ + '.', '')

#.............................................................................
#   test_filtersuite.py
