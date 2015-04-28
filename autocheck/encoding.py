# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2015-04-28.
#=============================================================================
#   encoding.py --- String output encoding/decoding
#
# inspired by Django but not with an emphasis on being strict but on retaining
# as much information as possible in the output
#=============================================================================
from __future__ import absolute_import, unicode_literals

import codecs
import locale
from io import StringIO

import six


try:
    encoding = locale.locale.getpreferredencoding().lower()
    codecs.lookup(encoding)
except Exception:
    encoding = 'ascii'

errors = 'backslashreplace'
errors_fallback = 'replace'


class ConsoleBuffer(StringIO):

    def write(self, s):
        super(ConsoleBuffer, self).write(smart_text(s))


def smart_text(s, encoding=encoding, errors=errors):
    if isinstance(s, six.text_type):
        return s
    if not isinstance(s, six.string_types):
        try:
            s = six.text_type(s, encoding, errors)
        except:
            if isinstance(s, Exception):
                s = ' '.join(smart_text(arg, encoding, errors)
                             for arg in s.args)
            else:
                s = six.text_type(s, encoding, errors_fallback)
    if isinstance(s, bytes):
        try:
            s = s.decode(encoding, errors)
        except:
            s = s.decode(encoding, errors_fallback)
    return s


def smart_bytes(s, encoding=encoding, errors=errors):
    if isinstance(s, bytes):
        return s
    if not isinstance(s, six.string_types):
        s = smart_text(s)
    try:
        s = s.encode(encoding, errors)
    except:
        s = s.encode(encoding, errors_fallback)
    return s

if six.PY2:
    smart_str = smart_bytes
else:
    smart_str = smart_text

#.............................................................................
#   encoding.py
