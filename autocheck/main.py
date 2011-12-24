# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   main.py --- Run tests automatically
#=============================================================================
import logging
import os
import signal
import sys

from autorunner import AutocheckObserver
from db import Database
from testrunner import TestRunner, TestProgram


log = logging.getLogger('autocheck')


class Unbuffered:
    
    def __init__(self, stream):
        self.stream = stream
    
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

def handle_term():
    def sighandler(signum, frame):
        os.kill(os.getpid(), signal.SIGINT)
    signal.signal(signal.SIGTERM, sighandler)

def single(args):
    sys.stdout=Unbuffered(sys.stdout)
    TestProgram(module=None, testRunner=TestRunner, argv=args, database=Database())

def autocheck(args):
    handle_term()
    root = AutocheckObserver('.', args, database=Database())
    log.debug('starting autocheck observer')
    while True:
        try:
            root.loop()
        except KeyboardInterrupt:
            if not root.kill_child():
                print >> sys.stderr, 'Got signal, exiting.'
                break

def main(args=sys.argv):
    if '--once' in args:
        if args[1] == '-m' and args[2] in ('autocheck', 'autocheck.main'):
            args[1:3] = []
        args.remove('--once')
        single(args)
    else:
        autocheck(args)

if __name__ == '__main__':
    if sys.argv[0].endswith('main.py'):
        sys.argv[0:1] = [os.path.abspath(sys.executable), '-m', 'autocheck.main']
    
    main()

#.............................................................................
#   main.py
