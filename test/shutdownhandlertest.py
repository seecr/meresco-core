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
