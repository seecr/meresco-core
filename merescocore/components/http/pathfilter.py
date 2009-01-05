## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from merescocore.framework.observable import Observable
from meresco.components.statistics import Logger

class PathFilter(Observable, Logger):
    def __init__(self, subPaths, excluding=[]):
        Observable.__init__(self)
        Logger.__init__(self)
        self._subPaths = subPaths
        if type(subPaths) == str:
            self._subPaths = [subPaths]
        self._excluding = excluding

    def handleRequest(self, path, *args, **kwargs):
        matchesSubPath = [subPath for subPath in self._subPaths if path.startswith(subPath)]
        matchesExcludedPath = [excludedPath for excludedPath in self._excluding if path.startswith(excludedPath)]
        if matchesSubPath and not matchesExcludedPath:
            self.log(path=matchesSubPath[0])
            return self.all.handleRequest(path=path, *args, **kwargs)
        return (f for f in [])

    def unknown(self, methodName, *args, **kwargs):
        return self.all.unknown(methodName, *args, **kwargs)
