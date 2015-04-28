# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-06-01.
#=============================================================================
#   tags.py --- Add tags to tests
#=============================================================================
from __future__ import absolute_import, unicode_literals

import operator
from functools import reduce


def tag(*tags):
    def decorator(test_item):
        test_item.__autocheck_tags__ = get_tags(test_item) | set(tags)
        return test_item
    return decorator


def add_tags(test_item, tags):
    all_tags = tuple(get_tags(test_item) | set(tags))
    return tag(*all_tags)(test_item)


def get_tags(test_item):
    tags = set()
    try:
        tags |= test_item.__autocheck_tags__
    except AttributeError:
        pass
    try:
        test_item = getattr(test_item, test_item._testMethodName)
    except AttributeError:
        pass
    try:
        test_item.__mro__
    except AttributeError:
        pass
    else:
        tags = reduce(operator.__or__, (
            getattr(cls, '__autocheck_tags__', set())
            for cls in test_item.__mro__
        ), tags)
    tags |= getattr(test_item, '__autocheck_tags__', set())
    return tags

#.............................................................................
#   tags.py
