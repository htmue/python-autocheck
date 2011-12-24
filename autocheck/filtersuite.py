# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-29.
#=============================================================================
#   filtersuite.py --- Filter test suites
#=============================================================================
from compat import unittest


def flatten_suite(suite):
    def flatten(suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                for t in flatten(test):
                    yield t
            else:
                yield test
    return unittest.TestSuite(flatten(suite))


def filter_suite(suite, database):
    full_suite = True
    if database is not None:
        flattened = flatten_suite(suite)
        candidates = database.candidates(flattened)
        if candidates:
            tests_to_run = [test for test in flattened if str(test) in candidates]
            if tests_to_run:
                suite = unittest.TestSuite(tests_to_run)
                full_suite = False
    return suite, full_suite


#.............................................................................
#   filtersuite.py
