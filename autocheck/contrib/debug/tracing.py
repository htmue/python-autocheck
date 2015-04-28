# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-11.
#=============================================================================
#   tracing.py --- Debug tracing support
#=============================================================================
from __future__ import absolute_import, unicode_literals

import functools
import logging
import types

import six


trace = logging.getLogger(__name__)
trace.debug('enabled')


def tracing(f, name, log=trace.debug):
    @functools.wraps(f)
    def traced_f(*args, **kwargs):
        log('[%#x]%s(%s,%s)', id(args[0]), name, args[1:], kwargs)
        result = f(*args, **kwargs)
        log('[%#x]%s(%s,%s) => %r', id(args[0]),
            name, args[1:], kwargs, result)
        return result
    return traced_f


class MetaTracer(type):

    def __new__(cls, classname, bases, classdict):
        log = logging.getLogger('%s.%s' % (classdict['__module__'], classname))
        classdict.setdefault('log', log)
        if trace.isEnabledFor(logging.DEBUG):
            for f in classdict:
                m = classdict[f]
                if isinstance(m, types.FunctionType):
                    classdict[f] = tracing(
                        m, '%s.%s' % (classname, f), log=log.debug)
        return type.__new__(cls, classname, bases, classdict)


class Tracer(six.with_metaclass(MetaTracer)):
    pass


def setLevel(level):  # noqa
    trace.setLevel(level)

#.............................................................................
#   tracing.py
