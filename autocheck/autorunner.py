# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   autorunner.py --- Run tests automatically
#=============================================================================
from __future__ import print_function

import os
import subprocess
import threading

from watchdog.events import RegexMatchingEventHandler
from watchdog.utils import has_attribute, unicode_paths

from .gitignore import GitIgnore


DEFAULT_FILEPATTERN = r'.*\.(py|txt|yaml|sql|html|js|css|feature|xml)$'

class AutocheckEventHandler(RegexMatchingEventHandler):
    
    def __init__(self, dir, args, filepattern=DEFAULT_FILEPATTERN, database=None):
        self._lock = threading.Lock()
        self.child = None
        self.args = args + ['--once']
        if is_django():
            os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
            self.args[0:1] = ['./manage.py', 'autocheck']
        for arg in args:
            if arg.startswith('--python='):
                self.args = [arg.split('=', 1)[1]] + self.args
        self.db = database
        self.gitignore = GitIgnore(dir)
        super(AutocheckEventHandler, self).__init__(regexes=[filepattern], ignore_directories=True, case_sensitive=False)
    
    def dispatch(self, event):
        paths = []
        if has_attribute(event, 'dest_path'):
            paths.append(unicode_paths.decode(event.dest_path))
        elif event.src_path:
            paths.append(unicode_paths.decode(event.src_path))
        
        if any(self.gitignore.match(p) for p in paths):
            return
        super(AutocheckEventHandler, self).dispatch(event)
    
    @property
    def child(self):
        with self._lock:
            return self._child
    
    @child.setter
    def child(self, child):
        with self._lock:
            self._child = child
    
    def kill_child(self):
        child = self.child
        if child is not None:
            return True
    
    def run_tests(self):
        print(' '.join(self.args))
        self.child = subprocess.Popen(self.args, close_fds=True)
        self.child.wait()
        returncode = self.child.returncode
        self.child = None
        if self.db is None:
            return False
        try:
            return self.db.should_run_again()
        finally:
            self.db.close()
    
    def on_any_event(self, event):
        while self.run_tests():
            pass


def is_django():
    if os.path.exists('manage.py'):
        with open('manage.py') as manage:
            for line in manage:
                if 'DJANGO_SETTINGS_MODULE' in line:
                    try:
                        import django
                    except ImportError:
                        return
                    return True

#.............................................................................
#   autorunner.py
