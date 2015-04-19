# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2012-09-02.
#=============================================================================
#   autocheck.py --- Autocheck command
#=============================================================================
from __future__ import absolute_import, print_function

import os, sys
from optparse import make_option

import django
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Run tests automatically'
    option_list = (
        make_option('--once', action='store_true', default=False,
            help='Single test run.'
        ),
        make_option('--no-verbose', action='store_false', dest='verbose', default=True,
            help='Do not run unittests verbose.'
        ),
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'
        ),
        make_option('-f', '--failfast', action='store_true', default=False,
            help='Stop on first failure.'
        ),
        make_option('-c', '--catch', action='store_true', default=False,
            help='Catch control-C and display results.'
        ),
        make_option('--no-buffer', action='store_false', dest='buffer', default=True,
            help='Do not buffer stdout and stderr during test runs.'
        ),
        make_option('-s', metavar='DIRECTORY', dest='start', default='.',
            help='Directory to start discovery (default: ".").'
        ),
        make_option('-p', metavar='PATTERN', dest='pattern',
            help='Pattern to match test files ("test*.py" default).'
        ),
        make_option('-t', metavar='DIRECTORY', dest='top_level', default='.',
            help='Top level directory of project (default: ".").'
        ),
    ) + BaseCommand.option_list
    if django.get_version() < '1.7':
        requires_model_validation = False
    else:
        requires_system_checks = False
    can_import_settings = False
    leave_locale_alone = True
    
    def handle(self, *args, **options):
        if options.pop('once'):
            self.once(*args, **options)
        else:
            self.autotest(*args, **options)
    
    def once(self, *args, **options):
        from autocheck.main import Unbuffered
        sys.stdout = Unbuffered(sys.stdout)
        from django.conf import settings
        from django.test.utils import get_runner
        verbosity = int(options.pop('verbosity'))
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=verbosity, **options)
        failures = test_runner.run_tests(args, **options)
        if failures:
            sys.exit(bool(failures))
    
    def autotest(self, *args, **options):
        import resource
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (4096, -1))
        except Exception, e:
            print(repr(e))
        settings = options['settings']
        if not settings and os.path.exists('test_settings.py'):
            settings = 'test_settings'
        os.environ['DJANGO_SETTINGS_MODULE'] = settings
        from autocheck.main import autocheck
        autocheck(sys.argv)


#.............................................................................
#   autocheck.py
