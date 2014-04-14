## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2013-2014 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2013 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
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

import sys
from sys import exit, argv
from os import remove
from os.path import isfile, join
from time import sleep
from signal import signal, SIGTERM, SIGINT, SIGUSR2, SIG_DFL, SIG_IGN
from functools import partial

from weightless.core import compose


class ShutdownHandler(object):
    def __init__(self, stateDir, server, reactor, exitOnError=True):
        self._server = server
        self._reactor = reactor
        self._runningMarkerFile = join(stateDir, 'running.marker')
        if isfile(self._runningMarkerFile):
            print "The '%s' process was not previously shutdown to a consistent persistent state." % argv[0]
            sys.stdout.flush()
            if exitOnError:
                print "NOT starting from an unknown state."
                exit(1)
        self._previouslyRegisteredHandlers = {}
        for signalnum in [SIGTERM, SIGINT, SIGUSR2]:
            self._previouslyRegisteredHandlers[signalnum] = signal(signalnum, self._handleShutdown)
        open(self._runningMarkerFile, 'w').write("written by registerShutdownHandler method in '%s' process" % argv[0])

    def _handleShutdown(self, signum, frame):
        self._reactor.addTimer(0, partial(self._deferredHandleShutdown, signum=signum))
        print 'scheduled for immediate shutdown'
        sys.stdout.flush()

    def _deferredHandleShutdown(self, signum):
        assert isfile(self._runningMarkerFile)
        list(compose(self._server.once.handleShutdown()))
        if signum == SIGUSR2:
            print 'state persisted'
        else:
            remove(self._runningMarkerFile)
            print 'shutdown completed'
        sys.stdout.flush()

        previousHandler = self._previouslyRegisteredHandlers[signum]
        if previousHandler not in [SIG_DFL, SIG_IGN, None]:
            print previousHandler
            previousHandler()
        if signum == SIGUSR2:
            return
        if signum == SIGINT:
            raise KeyboardInterrupt()
        else:
            exit(signum)

    def _sleep(self, t):
        sleep(t)

