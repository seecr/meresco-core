## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2013-2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Core"
#
# "Meresco Core" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Core" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Core"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from seecr.test import SeecrTestCase, CallTrace
from seecr.test.io import stdout_replaced

from os import kill, getpid
from os.path import join, isfile
from signal import getsignal
from signal import SIGUSR1, SIGINT, SIGTERM

from weightless.core import be, consume

from meresco.core import Observable
from meresco.core.processtools import registerShutdownHandler
from meresco.core.processtools.shutdownhandler import _ShutdownHandler, PERSIST_SIGNALS, SHUTDOWN_SIGNALS


class ShutdownHandlerTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self._shutdownHandler = None

    def tearDown(self):
        if self._shutdownHandler is not None:
            self._shutdownHandler.unregister()

        SeecrTestCase.tearDown(self)

    def _createShutdownHandler(self, *args, **kwargs):
        self._shutdownHandler = registerShutdownHandler(*args, **kwargs)

    def testInit(self):
        shutdownHandler = self._createShutdownHandler(stateDir=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'))
        self.assertTrue(isfile(join(self.tempdir, 'running.marker')))

    def testInitIfRunningMarkerStillThere(self):
        open(join(self.tempdir, 'running.marker'), 'w').write('already there')
        with stdout_replaced() as output:
            try:
                registerShutdownHandler(stateDir=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'))
                self.fail('should terminate')
            except SystemExit:
                print 'TODO: delegate to something else.'
                #pass

            self.assertTrue("process was not previously shutdown to a consistent persistent state.")
            self.assertTrue("NOT starting from an unknown state." in output.getvalue(), output.getvalue())

    def testShouldNotRegisteredTwice(self):
        self._createShutdownHandler(stateDir=self.tempdir, server='ignored', reactor='ignored')
        try:
            self._createShutdownHandler(stateDir=self.tempdir, server='ignored', reactor='ignored')
        except AssertionError, e:
            self.assertEquals('Handler already registered, aborting.', str(e))
        else:
            self.fail()

    def testShouldUnregister(self):
        # ... for testing purposes.
        def getRelevantHandlers():
            return [getsignal(sh) for sh in PERSIST_SIGNALS + SHUTDOWN_SIGNALS]  # SIGUSR2, SIGTERM, SIGINT

        persistable = CallTrace('Observer', emptyGeneratorMethods=['handleShutdown'])
        top = be((Observable(),
            (persistable,),
        ))
        reactor = CallTrace('reactor')

        pre = getRelevantHandlers()
        handler = registerShutdownHandler(stateDir=self.tempdir, server=top, reactor=reactor)

        _with = getRelevantHandlers()
        handler.unregister()

        post = getRelevantHandlers()

        # shutdownHandler set
        ourHandlerSet = set(_with).difference(set(pre))
        self.assertEquals(1, len(ourHandlerSet))
        ourHandler = ourHandlerSet.pop()

        # shutdownHandler removed on .unregister()
        self.assertEquals(pre, post)

        self.assertEquals('_handleShutdown', ourHandler.__func__.func_name)
        self.assertEquals(handler, ourHandler.__self__)

