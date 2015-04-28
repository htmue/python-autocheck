# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-06-01.
#=============================================================================
#   test_tags.py --- Tag support vows
#=============================================================================
from __future__ import absolute_import, unicode_literals

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

    def test_combines_tags_from_method_and_class(self):
        @tag('class')
        class Test(unittest.TestCase):

            @tag('method')
            def test_method(self):
                pass
        test_item = Test('test_method')

        get_tags(test_item) |should| be_equal_to(set(['class', 'method']))

    def test_combines_tags_from_class_and_superclass(self):
        @tag('super')
        class Super(unittest.TestCase):
            pass

        @tag('class')
        class Test(Super):

            def test_method(self):
                pass
        test_item = Test('test_method')

        get_tags(test_item) |should| be_equal_to(set(['class', 'super']))

    def test_combines_tags_from_method_and_superclass(self):
        @tag('super')
        class Super(unittest.TestCase):
            pass

        class Test(Super):

            @tag('method')
            def test_method(self):
                pass
        test_item = Test('test_method')

        get_tags(test_item) |should| be_equal_to(set(['method', 'super']))

    def test_combines_tags_from_class_and_mixin(self):
        @tag('mixin')
        class Mixin(object):
            pass

        @tag('class')
        class Test(Mixin, unittest.TestCase):

            def test_method(self):
                pass
        test_item = Test('test_method')

        get_tags(test_item) |should| be_equal_to(set(['class', 'mixin']))

    def test_combines_tags_from_class_superclass_and_mixin(self):
        @tag('mixin')
        class Mixin(object):
            pass

        @tag('super')
        class Super(unittest.TestCase):
            pass

        @tag('class')
        class Test(Mixin, Super):

            def test_method(self):
                pass
        test_item = Test('test_method')

        get_tags(test_item) |should| be_equal_to(
            set(['class', 'mixin', 'super']))

    def test_combines_tags_from_method_class_superclass_and_mixin(self):
        @tag('mixin')
        class Mixin(object):
            pass

        @tag('super')
        class Super(unittest.TestCase):
            pass

        @tag('class')
        class Test(Mixin, Super):

            @tag('method')
            def test_method(self):
                pass
        test_item = Test('test_method')

        get_tags(test_item) |should| be_equal_to(
            set(['class', 'method', 'mixin', 'super']))

    def test_does_not_mix_tags_from_different_classes_with_same_mixin(self):
        @tag('mixin')
        class Mixin(object):
            pass

        @tag('other')
        class Other(Mixin, unittest.TestCase):
            pass

        @tag('class')
        class Test(Mixin, unittest.TestCase):

            @tag('method')
            def test_method(self):
                pass
        test_item = Test('test_method')

        get_tags(test_item) |should| be_equal_to(
            set(['class', 'method', 'mixin']))


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
