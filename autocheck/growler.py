# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-05-13.
#=============================================================================
#   growler.py --- Growl notifier
#=============================================================================
from __future__ import absolute_import, unicode_literals

from os.path import dirname, join

from gntp.notifier import GrowlNotifier


class Notifier(object):

    def __init__(self, app_name='autocheck'):
        self.growl = GrowlNotifier(
            applicationName=app_name,
            notifications=['New Message'],
            defaultNotifications=['New Message']
        )
        self.growl.register()

    def notify(self, title, description, kind='pass', sticky=False):
        icon = open(
            join(dirname(__file__), 'images', kind + '.png'), 'rb').read()
        self.growl.notify(
            noteType='New Message',
            title=title,
            description=description,
            icon=icon,
            sticky=sticky,
        )

#.............................................................................
#   growler.py

# Smilies by Jamie Hill:
# http://thelucid.com/2007/07/30/autotest-growl-fail-pass-smilies/
