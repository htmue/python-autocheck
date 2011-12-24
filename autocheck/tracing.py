# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-11.
#=============================================================================
#   tracing.py --- Debug tracing support
#=============================================================================
import functools
import logging
import types


trace = logging.getLogger(__name__)
trace.debug('enabled')


def tracing(f, name, log=trace.debug):
    @functools.wraps(f)
    def traced_f(*args, **kwargs):
        log('[%#x]%s(%s,%s)', id(args[0]), name, args[1:], kwargs)
        result = f(*args, **kwargs)
        log('[%#x]%s(%s,%s) => %r', id(args[0]), name, args[1:], kwargs, result)
        return result
    return traced_f

class MetaTracer(type):
    
    def __new__(self, classname, bases, classdict):
        log = logging.getLogger('%s.%s' % (classdict['__module__'], classname))
        classdict.setdefault('log', log)
        if trace.isEnabledFor(logging.DEBUG):
            for f in classdict:
                m = classdict[f]
                if isinstance(m, types.FunctionType):
                    classdict[f] = tracing(m, '%s.%s' % (classname, f), log=log.debug)
        return type.__new__(self, classname, bases, classdict)

class Tracer(object):
    __metaclass__ = MetaTracer

def setLevel(level):
    trace.setLevel(level)

#.............................................................................
#   tracing.py
