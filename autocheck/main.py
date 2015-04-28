# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   main.py --- Run tests automatically
#=============================================================================
from __future__ import absolute_import, print_function, unicode_literals

import os
import signal
import sys
import time

from watchdog.observers import Observer

from .autorunner import AutocheckEventHandler, AutocheckWorker
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
    sys.stdout = Unbuffered(sys.stdout)
    TestProgram(
        module=None, testRunner=TestRunner, argv=args, database=Database())


def autocheck(args):
    handle_term()
    event_handler = AutocheckEventHandler()
    worker = AutocheckWorker(
        event_handler.queue, '.', args, database=Database())
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    try:
        worker.start()
    except KeyboardInterrupt:
        pass
    while True:
        try:
            time.sleep(111)
        except KeyboardInterrupt:
            if worker.child is None:
                print('Got signal, exiting.', file=sys.stderr)
                observer.stop()
                worker.stop()
                break
    observer.join()
    worker.join()


def main(args=sys.argv):
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
        if is_django():
            settings = None
            for i, arg in enumerate(args[1:]):
                if arg.startswith('--settings'):
                    if arg.startswith('--settings='):
                        settings = arg.split('=', 1)[0]
                    else:
                        settings = arg[i + 1]
                    break
            if not settings and os.path.exists('test_settings.py'):
                settings = 'test_settings'
            if settings:
                os.environ['DJANGO_SETTINGS_MODULE'] = settings
            args[0:1] = ['./manage.py', 'test']
        else:
            args += ['--once']
        for arg in args[:]:
            if arg.startswith('--python='):
                args = [arg.split('=', 1)[1]] + args
        autocheck(args)


def is_django():
    if os.path.exists('manage.py'):
        with open('manage.py') as manage:
            for line in manage:
                if 'DJANGO_SETTINGS_MODULE' in line:
                    try:
                        import django  # noqa
                    except ImportError:
                        return False
                    return True

if __name__ == '__main__':
    if sys.argv[0].endswith('main.py'):
        sys.argv[0:1] = [
            os.path.abspath(sys.executable), '-m', 'autocheck.main']

    main()

#.............................................................................
#   main.py
