# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   main.py --- Run tests automatically
#=============================================================================
from __future__ import print_function, unicode_literals

import os
import signal
import sys
import time

from watchdog.observers.fsevents import FSEventsObserver as Observer

from .autorunner import AutocheckEventHandler
from .db import Database
from .testrunner import TestRunner, TestProgram


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
    event_handler = AutocheckEventHandler('.', args, database=Database())
    try:
        event_handler.run_tests()
    except KeyboardInterrupt:
        pass
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            if not event_handler.kill_child():
                print('Got signal, exiting.', file=sys.stderr)
                observer.stop()
                break
    observer.join()

def main(args=sys.argv):
    import resource
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (4096, -1))
    except Exception as e:
        print(repr(e))
    if '--once' in args:
        if args[1] == '-m' and args[2] in ('autocheck', 'autocheck.main'):
            args[1:3] = []
        args.remove('--once')
        single(args)
    elif '--stats-flat' in args:
        database = Database()
        for test in database.stats():
            print('{time:f} {runs: >8}\t{suite}.{test}'.format(**test))
    elif '--stats' in args:
        database = Database()
        total_time = 0.0
        for suite in database.stats_grouped():
            print('{time:f} {suite}'.format(**suite))
            total_time += suite['time']
            for test in suite['tests']:
                print('\t{time:f} {runs: >8}\t{test}'.format(**test))
        print('total: {:f}'.format(total_time))
    else:
        autocheck(args)

if __name__ == '__main__':
    if sys.argv[0].endswith('main.py'):
        sys.argv[0:1] = [os.path.abspath(sys.executable), '-m', 'autocheck.main']
    
    main()

#.............................................................................
#   main.py
