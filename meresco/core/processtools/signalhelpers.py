## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2011-2014 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2011 Seek You Too (CQ2) http://www.cq2.nl
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

from signal import SIGINT, SIGTERM, SIG_IGN, SIG_DFL, signal, getsignal


def setSignalHandlers():
    if getsignal(SIGINT) == SIG_IGN:
        print 'SIGINT was ignored, restoring to defaulthandler'
        signal(SIGINT, SIG_DFL)

    if getsignal(SIGTERM) == SIG_IGN:
        print 'SIGTERM was ignored, restoring to defaulthandler'
        signal(SIGTERM, SIG_DFL)

