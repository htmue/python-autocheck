# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-29.
#=============================================================================
#   colorizer.py --- Colours
#=============================================================================
import os.path

import termstyle
import yaml


class ColourDecorator(object):
    """Used to decorate file-like objects' 'write' method to accept colours"""
    def __init__(self, stream):
        self.stream = stream
    
    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)
    
    def write(self, arg=None, colour=None):
        if arg:
            if colour is not None:
                arg = colour(arg)
        self.stream.write(arg)


class ColourWritelnDecorator(ColourDecorator):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self, stream):
        self.stream = stream
    
    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)
    
    def writeln(self, arg=None, colour=None):
        if arg:
            self.write(arg, colour=colour)
        self.write('\n') # text-mode streams translate to \r\n if needed


class ColourScheme(object):
    
    def __init__(self, scheme):
        if isinstance(scheme, basestring):
            filename = os.path.join(os.path.dirname(__file__), 'colourschemes', scheme + '.yaml')
            self.scheme = yaml.load(open(filename))
        else:
            self.scheme = scheme
    
    def __getattr__(self, key):
        if self.scheme is not None:
            colour = self.scheme.get(key)
            if isinstance(colour, basestring):
                return getattr(termstyle, colour)
            elif colour is None:
                return lambda x: x
            else:
                return compose(getattr(termstyle, c) for c in colour)

def compose(iterable):
    def compose(arg):
        for f in iterable:
            arg = f(arg)
        return arg
    return compose


#.............................................................................
#   colorizer.py