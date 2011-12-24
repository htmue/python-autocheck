# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   autorunner.py --- Run tests automatically
#=============================================================================
import logging
import os
import re
import subprocess
import threading

from db import Database
from observer.gitignore import GitIgnore
from observer.tree import TreeObserver


log = logging.getLogger(__name__)

DEFAULT_FILEPATTERN = re.compile(r'.*\.(py|txt|yaml|sql|html|js|css|feature)$')

class AutocheckObserver(TreeObserver):
    
    def __init__(self, dir, args, filepattern=DEFAULT_FILEPATTERN, database=None):
        self._lock = threading.Lock()
        self.child = None
        self.args = args + ['--once']
        for arg in args:
            if arg.startswith('--python='):
                self.args = [arg.split('=', 1)[1]] + self.args
        self.db = database
        super(AutocheckObserver, self).__init__(dir, filepattern, GitIgnore(dir))
    
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
            # child.terminate()
            # child.send_signal(signal.SIGINT)
            return True
    
    def run_tests(self):
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
    
    def action(self, entries):
        while self.run_tests():
            pass

#.............................................................................
#   autorunner.py
