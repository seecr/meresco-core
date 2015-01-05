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

from inspect import currentframe
from os import kill, getpid
from os.path import join, isfile
from signal import getsignal, signal
from signal import SIGINT, SIGTERM

from weightless.core import be

from weightless.io import Reactor

from meresco.core import Observable
from meresco.core.processtools import registerShutdownHandler, ShutdownFailedException
from meresco.core.processtools.shutdownhandler import SHUTDOWN_SIGNALS


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
        return self._shutdownHandler

    def testShouldWriteRunningMarkerOnInit(self):
        self._createShutdownHandler(statePath=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'))
        self.assertTrue(isfile(join(self.tempdir, 'running.marker')))

    def testShouldAbortInitWithExceptionIfRunningMarkerStillThere(self):
        # Subclassed SystemExit for ShutdownFailedException to ensure a service quits when left in an inconsistent state,
        # even if it needs to traverse "except (SystemExit, KeyboardInterrupt, AssertionError)" catch-statements.
        self.assertTrue(issubclass(ShutdownFailedException, SystemExit))

        with open(join(self.tempdir, 'running.marker'), 'w') as fp:
            fp.write('already there')

        with stdout_replaced() as output:
            try:
                self._createShutdownHandler(statePath=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'))
                self.fail('should terminate')
            except ShutdownFailedException:
                pass

            self.assertTrue("process was not previously shutdown to a consistent persistent state." in output.getvalue(), output.getvalue())
            self.assertTrue("NOT starting from an unknown state." in output.getvalue(), output.getvalue())

        with stdout_replaced() as output:
            try:
                self._createShutdownHandler(statePath=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'))
                self.fail('should terminate')
            except SystemExit:
                pass

    def testShouldContinueAfterCrashIfShutdownMustSucceedFlagFalse(self):
        with open(join(self.tempdir, 'running.marker'), 'w') as fp:
            fp.write('already there')

        with stdout_replaced() as output:
            try:
                self._createShutdownHandler(statePath=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'), shutdownMustSucceed=False)
            except SystemExit:
                self.fail('should not happen')

            self.assertTrue("process was not previously shutdown to a consistent persistent state." in output.getvalue(), output.getvalue())
            self.assertFalse("NOT starting from an unknown state." in output.getvalue(), output.getvalue())

    def testShouldNotRegisteredTwice(self):
        reactor = Reactor()
        trace = CallTrace('Observer')
        top = be((Observable(),
            (Observable(),  # Only once calls walk the observer tree.
                (trace,),
            ),
        ))
        self._createShutdownHandler(statePath=self.tempdir, server=top, reactor=reactor)

        try:
            registerShutdownHandler(statePath=self.tempdir, server='ignored', reactor='ignored')
        except AssertionError as e:
            self.assertEqual('Handler already registered, aborting.', str(e))
        else:
            self.fail()

        reactor.addTimer(0.01, lambda: None)
        with stdout_replaced() as output:
            try:
                kill(getpid(), SIGTERM)
                reactor.loop()
                self.fail('should terminate')
            except SystemExit as e:
                self.assertEqual((0,), e.args)

            self.assertTrue('Scheduled for immediate shutdown.\n' in output.getvalue(), output.getvalue())
            self.assertTrue('Shutdown completed.\n' in output.getvalue(), output.getvalue())

        # Only once!
        self.assertEqual(['handleShutdown'], trace.calledMethodNames())
        self.assertEqual(((), {}), (trace.calledMethods[0].args, trace.calledMethods[0].kwargs))

    def testShouldCallPreviouslyRegisteredSignalHandlersAfterHandleShutdown(self):
        reactor = Reactor()
        called = []
        def handleShutdown():
            called.append('handleShutdown')

        testCoName = currentframe().f_code.co_name
        def prevIntHandler(signum, frame):
            self.assertEqual(SIGINT, signum)
            self.assertEqual(testCoName, frame.f_code.co_name)
            called.append('prevIntHandler')

        trace = CallTrace('Observer', methods={'handleShutdown': handleShutdown})
        top = be((Observable(),
            (Observable(),  # Only once calls walk the observer tree.
                (trace,),
            ),
        ))

        origIntHandler = signal(SIGINT, prevIntHandler)
        try:
            shutdownHandler = registerShutdownHandler(statePath=self.tempdir, server=top, reactor=reactor)
            reactor.addTimer(0.01, lambda: None)
            with stdout_replaced() as output:
                try:
                    kill(getpid(), SIGINT)
                    reactor.loop()
                    self.fail('should terminate')
                except KeyboardInterrupt:
                    pass

                self.assertTrue('Scheduled for immediate shutdown.\n' in output.getvalue(), output.getvalue())
                self.assertTrue('Shutdown completed.\n' in output.getvalue(), output.getvalue())
        finally:
            shutdownHandler.unregister()
            signal(SIGINT, origIntHandler)

        self.assertEqual(['handleShutdown'], trace.calledMethodNames())
        self.assertEqual(((), {}), (trace.calledMethods[0].args, trace.calledMethods[0].kwargs))
        self.assertEqual(['handleShutdown', 'prevIntHandler'], called)

    def testShouldUnregister(self):
        # ... for testing purposes.
        def getRelevantHandlers():
            return [getsignal(sh) for sh in SHUTDOWN_SIGNALS]  # SIGTERM, SIGINT

        persistable = CallTrace('Observer', emptyGeneratorMethods=['handleShutdown'])
        top = be((Observable(),
            (persistable,),
        ))
        reactor = CallTrace('reactor')

        pre = getRelevantHandlers()
        handler = registerShutdownHandler(statePath=self.tempdir, server=top, reactor=reactor)

        _with = getRelevantHandlers()
        handler.unregister()

        post = getRelevantHandlers()

        # shutdownHandler set
        ourHandlerSet = set(_with).difference(set(pre))
        self.assertEqual(1, len(ourHandlerSet))
        ourHandler = ourHandlerSet.pop()

        # shutdownHandler removed on .unregister()
        self.assertEqual(pre, post)

        # shutdownHandler is who he's supposed to be.
        self.assertEqual('_handleShutdown', ourHandler.__func__.__name__)
        self.assertEqual(handler, ourHandler.__self__)

