# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-29.
#=============================================================================
#   extra_matchers.py --- Should-DSL extra matchers
#=============================================================================
from __future__ import absolute_import, unicode_literals

from should_dsl import matcher
from six.moves import zip_longest


@matcher
class EachEqual(object):
    name = 'each_be_equal_to'

    def __call__(self, expected):
        self._expected = expected
        return self

    def differ(self, given):
        for n, (left, right) in enumerate(zip_longest(given, self._expected)):
            if left != right:
                yield n + 1, left, right

    def match(self, given):
        diff = list(self.differ(given))
        self.diff = '\n\t'.join(
            '%d: %r is not equal to %r' % item for item in diff)
        return not diff

    def message_for_failed_should(self):
        return 'sequences differ\n\t' + self.diff


@matcher
def be_equal_to():
    return (lambda x, y: x == y, '%r is %sequal to %r')


@matcher
def be_in():
    return (lambda item, container: item in container, '%r is %sinto %r')

#.............................................................................
#   extra_matchers.py
