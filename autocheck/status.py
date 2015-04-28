# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-29.
#=============================================================================
#   status.py --- Test result status
#=============================================================================
from __future__ import print_function, unicode_literals


class Status(object):
    ordered = list()

    def __init__(self, key, name, name_plural, colour):
        self.key = key
        self.name = name
        self.name_plural = name_plural
        self.colour = colour
        self.ordered.append(self)


ok = Status('.', 'ok', None, 'ok')
fail = Status('F', 'FAIL', 'failures', 'fail')
error = Status('E', 'ERROR', 'errors', 'error')
skip = Status('s', 'skipped', 'skipped', 'skip')
expected_failure = Status(
    'x', 'expected failure', 'expectedFailures', 'expected_failure')
unexpected_success = Status(
    'u', 'unexpected success', 'unexpectedSuccesses', 'unexpected_success')

#.............................................................................
#   status.py
