## begin license ##
#
# "NBC+" also known as "ZP (ZoekPlatform)" is
#  initiated by Stichting Bibliotheek.nl to provide a new search service
#  for all public libraries in the Netherlands.
#
# Copyright (C) 2013 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2013 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
#
# This file is part of "NBC+ (Zoekplatform BNL)"
#
# "NBC+ (Zoekplatform BNL)" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "NBC+ (Zoekplatform BNL)" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "NBC+ (Zoekplatform BNL)"; if not, write to the Free Software
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
    def __init__(self, stateDir, server, reactor):
        self._server = server
        self._reactor = reactor
        self._runningMarkerFile = join(stateDir, 'running.marker')
        if isfile(self._runningMarkerFile):
            print "The '%s' process was not previously shutdown to a consistent persistent state; NOT starting from an unknown state." % argv[0]
            sys.stdout.flush()
            self._sleep(3600)
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
            previousHandler()
        if signum == SIGUSR2:
            return
        if signum == SIGINT:
            raise KeyboardInterrupt()
        else:
            exit(signum)

    def _sleep(self, t):
        sleep(t)

