## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2013-2014, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2013 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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
from signal import signal, SIGTERM, SIGINT, SIG_DFL, SIG_IGN
from functools import partial

try:
    from weightless.core import consume
except ImportError:
    # For compatibility with weightless-core 0.8.3
    from weightless.core import compose
    def consume(generator):
        for _ in compose(generator):
            pass


def registerShutdownHandler(**kwargs):
    return _ShutdownHandler(**kwargs)


class _ShutdownHandler(object):
    handlerRegistered = False

    def __init__(self, statePath, server, reactor, shutdownMustSucceed=True):
        if _ShutdownHandler.handlerRegistered:
            raise AssertionError('Handler already registered, aborting.')

        self._server = server
        self._reactor = reactor
        self._runningMarkerFile = join(statePath, 'running.marker')
        if isfile(self._runningMarkerFile):
            print("The '%s' process was not previously shutdown to a consistent persistent state." % argv[0])
            sys.stdout.flush()
            if shutdownMustSucceed:
                print("NOT starting from an unknown state.")
                sys.stdout.flush()
                raise ShutdownFailedException()

        self._register()

    def _register(self):
        self._previouslyRegisteredHandlers = {}
        for signalnum in SHUTDOWN_SIGNALS:
            self._previouslyRegisteredHandlers[signalnum] = signal(signalnum, self._handleShutdown)
        with open(self._runningMarkerFile, 'w') as fp:
            fp.write("written by registerShutdownHandler method in '%s' process" % argv[0])

        _ShutdownHandler.handlerRegistered = True

    def unregister(self):
        """For testing purposes"""
        for signalnum, previousHandler in list(self._previouslyRegisteredHandlers.items()):
            currentHandler = signal(signalnum, previousHandler)

        self._previouslyRegisteredHandlers.clear()
        _ShutdownHandler.handlerRegistered = False

    def _handleShutdown(self, signum, frame):
        self._reactor.addTimer(0, partial(self._deferredHandleShutdown, signum=signum, frame=frame))
        print('Scheduled for immediate shutdown.')
        sys.stdout.flush()

    def _deferredHandleShutdown(self, signum, frame):
        assert isfile(self._runningMarkerFile)
        consume(self._server.once.handleShutdown())
        remove(self._runningMarkerFile)
        print('Shutdown completed.')
        sys.stdout.flush()

        previousHandler = self._previouslyRegisteredHandlers[signum]
        if previousHandler not in [SIG_DFL, SIG_IGN, None]:
            previousHandler(signum, frame)
        if signum == SIGINT:
            raise KeyboardInterrupt()
        else:
            exit(0)


class ShutdownFailedException(SystemExit):
    pass


SHUTDOWN_SIGNALS = [SIGTERM, SIGINT]

