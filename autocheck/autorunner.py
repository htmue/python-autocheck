# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-12.
#=============================================================================
#   autorunner.py --- Run tests automatically
#=============================================================================
from __future__ import absolute_import, print_function, unicode_literals

import hashlib
import os
import shelve
import subprocess
import threading
import time
from contextlib import closing
from functools import partial

from six.moves import map
from six.moves.queue import Queue, Empty
from watchdog.events import RegexMatchingEventHandler
from watchdog.utils import has_attribute, unicode_paths


DEFAULT_FILEPATTERN = r'.*\.(py|txt|yaml|sql|html|js|css|feature|xml)$'


class AutocheckEventHandler(RegexMatchingEventHandler):

    def __init__(self, filepattern=DEFAULT_FILEPATTERN):
        self.queue = Queue()
        super(AutocheckEventHandler, self).__init__(
            regexes=[filepattern], ignore_directories=True,
            case_sensitive=False)

    def on_any_event(self, event):
        self.queue.put(event)


class AutocheckWorker(threading.Thread):

    def __init__(self, queue, dir, args, database=None, sleep=1, timeout=1):
        self._child_lock = threading.Lock()
        self._should_run_lock = threading.Lock()
        self.child = None
        self.should_run = True
        self.db = database
        self.queue = queue
        self.sleep = sleep
        self.timeout = timeout
        self.args = args
        super(AutocheckWorker, self).__init__(name='autocheck-worker')
        self.daemon = True

    def run(self):
        self.run_tests_while_pending()
        while self.should_run:
            self.check_run(self.collect_events())

    def collect_events(self):
        try:
            yield self.queue.get(timeout=self.timeout)
        except Empty:
            pass
        else:
            time.sleep(self.sleep)
            timeout = time.time() + self.timeout
            while time.time() < timeout:
                try:
                    yield self.queue.get_nowait()
                except Empty:
                    break

    def check_run(self, events):
        events = set(get_file_event_paths(events))
        if events:
            if self.filter_changed(events - self.get_git_ignored()):
                self.run_tests_while_pending()

    def get_git_ignored(self):
        try:
            output = subprocess.check_output(
                'git ls-files --others --ignored --exclude-standard'.split())
        except subprocess.CalledProcessError:
            output = ''
        return frozenset(map(unicode_paths.decode, output.splitlines()))

    def filter_changed(self, paths):
        with closing(shelve.open('.autocheck.fileinfo')) as fileinfo_db:
            return set(map(partial(self.file_changed, fileinfo_db), paths))

    def file_changed(self, fileinfo_db, path):
        old_stats, old_sha1 = fileinfo_db.setdefault(path, (None, None))
        if not os.path.exists(path):
            del fileinfo_db[path]
            return True
        new_stats = os.stat(path)
        if old_stats != new_stats:
            new_sha1 = file_sha1(path)
            fileinfo_db[path] = new_stats, new_sha1
            return old_sha1 != new_sha1

    def stop(self):
        self.should_run = False

    @property
    def should_run(self):
        with self._should_run_lock:
            return self._should_run

    @should_run.setter
    def should_run(self, should_run):
        with self._should_run_lock:
            self._should_run = should_run

    @property
    def child(self):
        with self._child_lock:
            return self._child

    @child.setter
    def child(self, child):
        with self._child_lock:
            self._child = child

    def run_tests(self):
        print(' '.join(self.args))
        self.child = subprocess.Popen(self.args, close_fds=True)
        self.child.wait()
        self.child = None
        if self.db is None:
            return False
        try:
            return self.db.should_run_again()
        finally:
            self.db.close()

    def run_tests_while_pending(self):
        while self.run_tests():
            pass
        if self.queue.empty():
            print('(waiting...)')


def get_file_event_paths(events):
    for event in events:
        for key in ('dest_path', 'src_path'):
            if has_attribute(event, key):
                path = unicode_paths.decode(getattr(event, key))
                if not (path.startswith('.autocheck.') or os.path.isdir(path)):
                    yield os.path.relpath(path)


def file_sha1(path):
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                return sha1.hexdigest()
            sha1.update(data)

#.............................................................................
#   autorunner.py
