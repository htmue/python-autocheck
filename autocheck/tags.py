# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-06-01.
#=============================================================================
#   tags.py --- Add tags to tests
#=============================================================================
from .compat import unittest


def tag(*tags):
    def decorator(test_item):
        test_item.__autocheck_tags__ = set(tags)
        return test_item
    return decorator

def add_tags(test_item, tags):
    all_tags = tuple(get_tags(test_item) | set(tags))
    return tag(*all_tags)(test_item)

def get_tags(test_item):
    if isinstance(test_item, unittest.TestCase):
        try:
            return test_item.__autocheck_tags__
        except AttributeError:
            test_item = getattr(test_item, test_item._testMethodName)
    return getattr(test_item, '__autocheck_tags__', set())


#.............................................................................
#   tags.py
