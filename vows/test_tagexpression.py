# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-06-01.
#=============================================================================
#   test_tagexpression.py --- Tag expression vows
#=============================================================================
from __future__ import absolute_import, unicode_literals

import os.path

import six
import yaml
from should_dsl import should

from autocheck.compat import unittest
from autocheck.tagexpression import (
    TagExpression, TagNode, TrueNode, FalseNode, NegationNode, AndNode, OrNode
)


with open(os.path.splitext(__file__)[0] + '.yaml') as f:
    test_examples = yaml.load(f)


class TagExpressionVowsMeta(type):

    def __new__(self, classname, bases, classdict):
        for key, test in six.iteritems(test_examples):
            for test_in, test_result in test['examples']:
                test_name = '_'.join(
                    ['test', 'example', 'with', key.replace(' ', '_')]
                    + (test_in if test_in else ['empty']))
                define_method(
                    classdict, test['groups'], test_in, test_result, test_name)
        return type.__new__(self, classname, bases, classdict)


def define_method(classdict, groups, test_in, test_result, test_name):
    def runTest(self):
        tags = TagExpression()
        for group in groups:
            tags.parse_and_add(group)
        tags.match(test_in) |should| be(test_result)
    runTest.__name__ = str(test_name)
    classdict[test_name] = runTest


class TagExpressionVows(
        six.with_metaclass(TagExpressionVowsMeta, unittest.TestCase)):

    def test_always_matches_when_empty(self):
        tags = TagExpression()
        result = tags.match(())
        result |should| be(True)

    def test_parses_tag(self):
        tags = TagExpression()
        node = tags.parse('@tag_name')
        node |should| be_instance_of(TagNode)
        node.name |should| be_equal_to('tag_name')

    def test_parses_negated_tag(self):
        tags = TagExpression()
        node = tags.parse('~@tag_name')
        node |should| be_instance_of(NegationNode)
        node.child |should| be_instance_of(TagNode)
        node.child.name |should| be_equal_to('tag_name')

    def test_parses_comma_separated_group_as_or_expression(self):
        tags = TagExpression()
        node = tags.parse('@tag_1,~@tag_2,@tag_3')

        node |should| be_instance_of(OrNode)

        node_1, node_2, node_3 = node.child_nodes

        node_1 |should| be_instance_of(TagNode)
        node_1.name |should| be_equal_to('tag_1')

        node_2 |should| be_instance_of(NegationNode)
        node_2.child |should| be_instance_of(TagNode)
        node_2.child.name |should| be_equal_to('tag_2')

        node_3 |should| be_instance_of(TagNode)
        node_3.name |should| be_equal_to('tag_3')

    def test_combines_parsed_expressions_to_and_expression(self):
        tags = TagExpression()
        tags.parse_and_add('@tag_0')

        tags.and_node |should| be_instance_of(AndNode)
        child_nodes = tags.and_node.child_nodes
        len(child_nodes) |should| be(1)
        child_nodes[0] |should| be_instance_of(TagNode)
        child_nodes[0].name |should| be_equal_to('tag_0')


class TagNodeVows(unittest.TestCase):

    def test_matches_when_value_is_in_testee(self):
        node = TagNode('name')
        result = node.match(('name', 'other'))
        result |should| be(True)

    def test_does_not_matche_when_value_is_not_in_testee(self):
        node = TagNode('name')
        result = node.match(('other', 'value'))
        result |should| be(False)


class TrueNodeVows(unittest.TestCase):

    def test_always_matches(self):
        node = TrueNode()
        result = node.match(())
        result |should| be(True)


class FalseNodeVows(unittest.TestCase):

    def test_never_matches(self):
        node = FalseNode()
        result = node.match(())
        result |should| be(False)


class NegationNodeVows(unittest.TestCase):

    def test_matches_when_child_does_not_match(self):
        node = NegationNode(FalseNode())
        result = node.match(())
        result |should| be(True)

    def test_does_not_match_when_child_does(self):
        node = NegationNode(TrueNode())
        result = node.match(())
        result |should| be(False)


class AndNodeVows(unittest.TestCase):

    def test_matches_when_all_child_nodes_do(self):
        node = AndNode((TrueNode(), TrueNode()))
        result = node.match(())
        result |should| be(True)

    def test_does_not_match_when_one_child_does_not(self):
        node = AndNode((TrueNode(), FalseNode(), TrueNode()))
        result = node.match(())
        result |should| be(False)

    def test_can_add_child_node(self):
        node = AndNode()
        node_1, node_2 = TrueNode(), FalseNode()
        node.add_child(node_1)
        node.add_child(node_2)
        node.child_nodes |should| be_equal_to([node_1, node_2])


class OrNodeVows(unittest.TestCase):

    def test_matches_when_at_least_one_child_does(self):
        node = OrNode((FalseNode(), TrueNode(), FalseNode()))
        result = node.match(())
        result |should| be(True)

    def test_does_not_match_when_no_child_does(self):
        node = AndNode((FalseNode(), FalseNode()))
        result = node.match(())
        result |should| be(False)


#.............................................................................
#   test_tagexpression.py
