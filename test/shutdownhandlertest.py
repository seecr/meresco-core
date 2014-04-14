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

from os.path import join, isfile

from meresco.core.processtools import registerShutdownHandler
from meresco.core.shutdownhandler import ShutdownHandler


class ShutdownHandlerTest(SeecrTestCase):
    def testInit(self):
        shutdownHandler = registerShutdownHandler(stateDir=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'))
        self.assertTrue(isfile(join(self.tempdir, 'running.marker')))

    def testInitIfRunningMarkerStillThere(self):
        original_sleep = ShutdownHandler._sleep
        sleepQueue = []
        ShutdownHandler._sleep = lambda self, t: sleepQueue.append(t)
        open(join(self.tempdir, 'running.marker'), 'w').write('already there')
        with stdout_replaced() as output:
            try:
                registerShutdownHandler(stateDir=self.tempdir, server=CallTrace('server'), reactor=CallTrace('reactor'))
                self.fail('should terminate')
            except SystemExit:
                self.assertEquals(1, len(sleepQueue))
            finally:
                ShutdownHandler._sleep = original_sleep
        self.assertTrue("process was not previously shutdown to a consistent persistent state; NOT starting from an unknown state." in output.getvalue(), output.getvalue())
