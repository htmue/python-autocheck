# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   test_colorizer.py --- Colorizer vows
#=============================================================================
from __future__ import unicode_literals, absolute_import

from io import StringIO

import termstyle
from should_dsl import should

from autocheck.colorizer import (
    ColourWritelnDecorator, ColourDecorator, ColourScheme
)
from autocheck.compat import unittest
from autocheck.testrunner import TestResult


class ColourTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        termstyle.Style.enabled |should| be(True)


class ColourDecoratorTest(ColourTestCase):

    def test_writes_arg_unchanged_without_colour(self):
        stream = ColourDecorator(StringIO())
        stream.write('{*}')
        stream.stream.getvalue() |should| be_equal_to('{*}')

    def test_wraps_arg_in_colour(self):
        stream = ColourDecorator(StringIO())
        stream.write('{*}', colour=termstyle.italic)
        stream.stream.getvalue() |should| be_equal_to(
            termstyle.italic('{*}'))


class ColourWritelnDecoratorTest(ColourTestCase):

    def test_writes_arg_as_line_without_colour(self):
        stream = ColourWritelnDecorator(StringIO())
        stream.writeln('{*}')
        stream.stream.getvalue() |should| be_equal_to('{*}\n')

    def test_wraps_arg_as_line_in_colour(self):
        stream = ColourWritelnDecorator(StringIO())
        stream.writeln('{*}', colour=termstyle.red)
        stream.stream.getvalue() |should| be_equal_to(
            termstyle.red('{*}') + '\n')


class ColourSchemeTest(ColourTestCase):

    def test_translates_names_to_termstyle_colours(self):
        scheme = ColourScheme(dict(ok='green'))
        scheme.ok |should| be(termstyle.green)

    def test_translates_sequences_of_styles_single_callable(self):
        scheme = ColourScheme(dict(blue_italic=('blue', 'italic')))
        scheme.blue_italic('{*}') |should| be_equal_to(
            termstyle.italic(termstyle.blue('{*}')))

    def test_can_load_colours_from_yaml_file_by_scheme_name(self):
        scheme = ColourScheme('light')
        scheme.ok |should| be(termstyle.green)

    def test_returns_always_None_if_no_scheme_given(self):
        scheme = ColourScheme(None)
        scheme.ok |should| be(None)


class ColourTestResultTest(ColourTestCase):

    def test_is_subclass_of_unittest_TestResult(self):
        TestResult() |should| be_instance_of(unittest.TestResult)

    def test_uses_colourscheme_from_yaml_file(self):
        result = TestResult(colourscheme='light')
        result.scheme.ok |should| be_equal_to(termstyle.green)


#.............................................................................
#   test_colorizer.py
