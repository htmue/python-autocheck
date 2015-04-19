# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-06-01.
#=============================================================================
#   test_tags.py --- Tag support vows
#=============================================================================
from should_dsl import should
from six.moves import map

from autocheck.compat import unittest
from autocheck.tagexpression import TagExpression
from autocheck.tags import tag, get_tags


class TagDecoratorVows(unittest.TestCase):
    
    def test_markes_test_item_by_test_case_decorator(self):
        @tag('include')
        class Test(unittest.TestCase):
            def test_method(self):
                pass
        test_item = Test('test_method')
        
        get_tags(test_item) |should| be_equal_to(set(['include']))
    
    def test_markes_test_item_by_test_method_decorator(self):
        class Test(unittest.TestCase):
            @tag('include')
            def test_method(self):
                pass
        test_item = Test('test_method')
        
        get_tags(test_item) |should| be_equal_to(set(['include']))


class TagFilterVows(unittest.TestCase):
    
    def test_includes_by_test_case_decorator(self):
        @tag('include')
        class Test(unittest.TestCase):
            def test_method(self):
                pass
        suite = unittest.TestSuite([Test('test_method')])
        tags = TagExpression('@include')
        
        filtered = tags.filter_suite(suite)
        
        map(str, filtered) |should| each_be_equal_to([
            'test_method (vows.test_tags.Test)',
        ])
    
    def test_excludes_by_test_case_decorator(self):
        @tag('include')
        class Test(unittest.TestCase):
            def test_method(self):
                pass
        suite = unittest.TestSuite([Test('test_method')])
        tags = TagExpression('~@include')
        
        filtered = tags.filter_suite(suite)
        
        map(str, filtered) |should| each_be_equal_to([])
    
    def test_includes_by_test_method_decorator(self):
        class Test(unittest.TestCase):
            @tag('include')
            def test_method(self):
                pass
        suite = unittest.TestSuite([Test('test_method')])
        tags = TagExpression('@include')
        
        filtered = tags.filter_suite(suite)
        
        map(str, filtered) |should| each_be_equal_to([
            'test_method (vows.test_tags.Test)',
        ])
    
    def test_excludes_by_test_method_decorator(self):
        class Test(unittest.TestCase):
            @tag('include')
            def test_method(self):
                pass
        suite = unittest.TestSuite([Test('test_method')])
        tags = TagExpression('~@include')
        
        filtered = tags.filter_suite(suite)
        
        map(str, filtered) |should| each_be_equal_to([])


#.............................................................................
#   test_tags.py
