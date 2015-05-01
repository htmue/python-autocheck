# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-28.
#=============================================================================
#   db.py --- Tests database
#=============================================================================
from __future__ import absolute_import, print_function, unicode_literals

import datetime
import functools
import hashlib
import inspect
import os
import re
import shutil
import sqlite3
from contextlib import contextmanager

import six
from six.moves import zip

from .status import Status, ok


try:
    import pytz
except ImportError:
    have_pytz = False
else:
    have_pytz = True


class DatabaseError(Exception):
    pass


class DoesNotExist(DatabaseError):
    pass


class RunDoesNotExist(DoesNotExist):
    pass


class ResultDoesNotExist(DoesNotExist):
    pass


class TestDoesNotExist(DoesNotExist):
    pass


def with_cursor(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        cursor = kwargs.pop('cursor', None)
        if cursor is None:
            with self.transaction() as cursor:
                return method(self, cursor, *args, **kwargs)
        else:
            return method(self, cursor, *args, **kwargs)
    return wrapper


class Database(object):
    _TABLES = dict(

        run='''run(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started TIMESTAMP,
            finished TIMESTAMP,
            wasSuccessful BOOLEAN,
            testsRun INTEGER,
            full BOOLEAN,
            errors INTEGER,
            failures INTEGER,
            skipped INTEGER,
            expectedFailures INTEGER,
            unexpectedSuccesses INTEGER
        )''',

        test='''test(
            name VARCHAR PRIMARY KEY,
            test VARCHAR,
            suite VARCHAR,
            hash VARCHAR,
            runs INTEGER,
            average_time TIMEDELTA
        )''',

        result='''result(
            name VARCHAR REFERENCES test(name),
            started TIMESTAMP,
            finished TIMESTAMP,
            run_id INTEGER REFERENCES run(id),
            status VARCHAR
        )''',

        version='''version(
            id VARCHAR PRIMARY KEY
        )''',

    )
    name_re = re.compile(r'(?P<test>[^\s]+)\s+\((?P<suite>[^)]+)\)')
    version = '1'

    def __init__(self, path=None, basedir=None, name='.autocheck.db'):
        if path is None:
            basedir = os.getcwd() if basedir is None else basedir
            self.path = os.path.join(basedir, name)
        else:
            self.path = path
        self.connection = None
        self.current_run_id = None

    def _connect(self):
        self.connection = sqlite3.connect(
            self.path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        self.connection.row_factory = sqlite3.Row

    def connect(self):
        self._connect()
        current_version = self.current_version()
        if current_version != self.version:
            self.migrate(current_version)

    def close(self):
        self.connection.close()
        self.connection = None

    @property
    def is_connected(self):
        return self.connection is not None

    def ensure_connection(self):
        if not self.is_connected:
            self.connect()
            self.setup()

    @contextmanager
    def transaction(self):
        self.ensure_connection()
        try:
            yield self.connection.cursor()
        except:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    @with_cursor
    def current_version(self, cursor):
        self.create_table('version', cursor=cursor)
        try:
            cursor.execute('SELECT id FROM version ORDER BY id DESC LIMIT 1')
        except sqlite3.OperationalError:
            return '0'
        row = cursor.fetchone()
        if row is None:
            cursor.execute(
                'INSERT INTO version(id) VALUES (?)', [self.version])
            return self.version
        return row[0]

    def migrate(self, current_version):
        print('migrating {} -> {} ...'.format(
            current_version, self.version), end='')
        self.close()
        new_path = '{}.bak-{}-{}'.format(self.path,
                                         current_version, self.version)
        os.rename(self.path, new_path)
        shutil.copy2(new_path, self.path)
        self._connect()
        if current_version == '0':
            self.migrate_0_1()
        print('done.')

    @with_cursor
    def migrate_0_1(self, cursor):
        self.create_table('version', cursor=cursor)
        cursor.execute('INSERT INTO version(id) VALUES (?)', [self.version])
        cursor.execute('ALTER TABLE test ADD COLUMN test VARCHAR')
        cursor.execute('ALTER TABLE test ADD COLUMN suite VARCHAR')
        cursor.execute('SELECT name FROM test')
        for row in cursor.fetchall():
            name = row[0]
            data = self.name_re.match(name).groupdict()
            data['name'] = name
            cursor.execute(
                'UPDATE test SET test=:test, suite=:suite WHERE name=:name',
                data)

    @with_cursor
    def setup(self, cursor):
        cursor.execute('PRAGMA foreign_keys = ON')
        for name in self._TABLES:
            self.create_table(name, cursor=cursor)

    @with_cursor
    def create_table(self, cursor, name):
        cursor.execute('CREATE TABLE IF NOT EXISTS %s' % self._TABLES[name])

    @with_cursor
    def add_run(self, cursor):
        cursor.execute('INSERT INTO run(started) VALUES (?)', [self.utcnow()])
        self.current_run_id = cursor.lastrowid

    @property
    def total_runs(self):
        with self.transaction() as cursor:
            cursor.execute('SELECT count(*) FROM run')
            count = cursor.fetchone()[0]
        return count

    @with_cursor
    def get_run(self, cursor, run_id=None):
        if run_id is None:
            run_id = self.current_run_id
        if run_id is None:
            raise RunDoesNotExist()
        cursor.execute('SELECT * FROM run WHERE id = ?', [run_id])
        run = cursor.fetchone()
        if run is None:
            raise RunDoesNotExist(run_id)
        return Row(run)

    @with_cursor
    def get_test(self, cursor, name):
        cursor.execute('SELECT * FROM test WHERE name=?', (name,))
        test = cursor.fetchone()
        if test is None:
            raise TestDoesNotExist(name)
        return Row(test)

    @with_cursor
    def get_or_create_test(self, cursor, test_object):
        name = str(test_object)
        data = self.name_re.match(name).groupdict()
        try:
            test = self.get_test(name, cursor=cursor)
        except TestDoesNotExist:
            cursor.execute(
                'INSERT INTO test(name,test,suite,hash,runs,average_time) '
                'VALUES (?,?,?,?,?,?)',
                (name, data['test'], data['suite'],
                 source_hash(test_object), 0, 0))
            test = self.get_test(name, cursor=cursor)
        return test

    @with_cursor
    def add_result(self, cursor, test_object, started, finished, status):
        test = self.get_or_create_test(test_object, cursor=cursor)
        cursor.execute(
            'INSERT INTO result(run_id,name,started,finished,status) '
            'VALUES (?,?,?,?,?)',
            (self.current_run_id, test['name'], started, finished, status))
        runs = test['runs'] + 1
        average_time = test['average_time']
        if status == ok.key:
            if average_time is None:
                average_time = finished - started
            else:
                total_time = average_time * (runs - 1) + (finished - started)
                average_time = total_time / runs
        cursor.execute(
            'UPDATE test SET runs=?,hash=?,average_time=? WHERE name=?',
            (runs, source_hash(test_object), average_time, str(test_object)))

    @with_cursor
    def add_results(self, cursor, results):
        for test_object, started, finished, status in results:
            self.add_result(test_object, self.to_utc(
                started), self.to_utc(finished), status, cursor=cursor)

    @with_cursor
    def get_last_result(self, cursor, name):
        cursor.execute(
            'SELECT * FROM result WHERE name=? ORDER BY finished DESC LIMIT 1',
            (name,))
        result = cursor.fetchone()
        if result is None:
            raise ResultDoesNotExist(name)
        return Row(result)

    @with_cursor
    def total_runs_by_test_name(self, cursor, name):
        return self.get_test(name, cursor=cursor)['runs']

    @with_cursor
    def get_result_count(self, cursor, run_id, status=None):
        if status is None:
            cursor.execute(
                'SELECT count(*) FROM result WHERE run_id=?', [run_id])
        else:
            cursor.execute(
                'SELECT count(*) FROM result WHERE status=? AND run_id=?',
                (status, run_id))
        return cursor.fetchone()[0]

    @with_cursor
    def get_result_counts(self, cursor, run_id):
        for status in Status.ordered:
            if status.name != ok.name:
                result_count = self.get_result_count(
                    run_id, status.key, cursor=cursor)
                yield status.name_plural, result_count

    @with_cursor
    def finish_run(self, cursor, full):
        run_id = self.current_run_id
        data = dict(self.get_result_counts(run_id, cursor=cursor))
        data.update(
            run_id=run_id,
            finished=self.utcnow(),
            wasSuccessful=data['errors'] == data['failures'] == 0,
            testsRun=self.get_result_count(run_id, cursor=cursor),
            full=full,
        )
        cursor.execute('''UPDATE run SET
            finished=:finished,
            wasSuccessful=:wasSuccessful,
            testsRun=:testsRun,
            full=:full,
            errors=:errors,
            failures=:failures,
            skipped=:skipped,
            expectedFailures=:expectedFailures,
            unexpectedSuccesses=:unexpectedSuccesses WHERE id=:run_id''', data)
        run = self.get_run(run_id, cursor=cursor)
        self.clean_history(cursor=cursor)
        return run

    @with_cursor
    def get_last_run_id(self, cursor, where=''):
        cursor.execute(
            'SELECT id FROM run %s ORDER BY finished DESC LIMIT 1' % where)
        run_id = cursor.fetchone()
        if run_id is not None:
            return run_id[0]

    @with_cursor
    def get_last_successful_run_id(self, cursor):
        return self.get_last_run_id('WHERE wasSuccessful=1', cursor=cursor)

    @with_cursor
    def get_last_successful_full_run_id(self, cursor):
        return self.get_last_run_id(
            'WHERE wasSuccessful=1 AND full=1', cursor=cursor)

    @with_cursor
    def get_last_run_ids(self, cursor):
        return (
            self.get_last_run_id(cursor=cursor),
            self.get_last_successful_run_id(cursor=cursor),
            self.get_last_successful_full_run_id(cursor=cursor),
        )

    @with_cursor
    def collect_results_after(self, cursor, run_id, status=ok.key,
                              exclude=True):
        cursor.execute('''SELECT DISTINCT name FROM result WHERE run_id IN (
            SELECT id FROM run WHERE started>(
                SELECT started FROM run WHERE id=?
            )) AND status%s?''' % ('=', '!=')[bool(exclude)], (run_id, status))
        for row in cursor.fetchall():
            yield row[0]

    @with_cursor
    def failures(self, cursor):
        last, successful, full = self.get_last_run_ids(cursor=cursor)
        if last != successful:
            return set(self.collect_results_after(full, cursor=cursor))
        else:
            return set()

    @with_cursor
    def source_has_changed(self, cursor, test_object):
        new_hash = source_hash(test_object)
        try:
            old_hash = self.get_test(str(test_object), cursor=cursor)['hash']
        except TestDoesNotExist:
            return True
        else:
            return old_hash != new_hash

    @with_cursor
    def collect_changes(self, cursor, tests):
        for test_object in tests:
            if self.source_has_changed(test_object, cursor=cursor):
                yield str(test_object)

    @with_cursor
    def candidates(self, cursor, tests):
        failures = self.failures(cursor=cursor)
        changes = set(self.collect_changes(tests, cursor=cursor))
        return failures | changes

    @with_cursor
    def should_run_again(self, cursor):
        last, successful, full = self.get_last_run_ids(cursor=cursor)
        if last is None:
            return False
        elif last != successful:
            return False
        elif last == full:
            return False
        else:
            return True

    @with_cursor
    def clean_history(self, cursor):
        run_id = self.get_last_successful_full_run_id(cursor=cursor)
        cursor.execute(
            'DELETE FROM result WHERE finished'
            ' < (SELECT started FROM run WHERE id=?)',
            (run_id,))
        cursor.execute(
            'DELETE FROM run WHERE'
            ' (SELECT count(*) FROM result WHERE run_id=run.id)=0')

    @with_cursor
    def stats(self, cursor, suite=None):
        if suite is None:
            cursor.execute('SELECT * FROM test ORDER BY average_time')
        else:
            cursor.execute(
                'SELECT * FROM test WHERE suite=? ORDER BY average_time',
                [suite])
        for row in cursor.fetchall():
            data = dict(zip(row.keys(), row))
            data['time'] = data['average_time'].total_seconds()
            yield data

    @with_cursor
    def stats_grouped(self, cursor):
        cursor.execute(
            'SELECT suite, total(average_time) as time FROM test '
            'GROUP BY suite ORDER BY time')
        for row in cursor.fetchall():
            suite = dict(zip(row.keys(), row))
            suite['tests'] = list(
                self.stats(cursor=cursor, suite=suite['suite']))
            yield suite

    def to_utc(self, datetime):
        return pytz.utc.localize(datetime) if have_pytz else datetime

    def utcnow(self):
        return self.to_utc(datetime.datetime.utcnow())


class Row(object):

    def __init__(self, row):
        self._row = row

    def __getitem__(self, key):
        return self._row[str(key)]


def source_hash(test_object):
    try:
        test_method = getattr(test_object, test_object._testMethodName)
    except AttributeError:
        return ''
    try:
        source = test_method.__self__.getsource()
    except AttributeError:
        source = inspect.getsource(test_method)
    if six.PY3:
        source = source.encode('utf-8')
    return hashlib.sha1(source).hexdigest()


def timedelta_to_float(delta):
    if hasattr(delta, 'total_seconds'):
        return delta.total_seconds()
    else:
        seconds = delta.seconds + delta.days * 24. * 3600.
        return (delta.microseconds + (seconds * 10**6)) / 10**6


def adapt_timedelta(delta):
    return str(timedelta_to_float(delta))


def convert_timedelta(s):
    return datetime.timedelta(seconds=float(s))

sqlite3.register_adapter(datetime.timedelta, adapt_timedelta)
sqlite3.register_converter(str('timedelta'), convert_timedelta)


def convert_boolean(s):
    return bool(int(s))

sqlite3.register_converter(str('boolean'), convert_boolean)

#.............................................................................
#   db.py
