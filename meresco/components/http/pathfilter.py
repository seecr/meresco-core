# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2010 Stichting Kennisnet http://www.kennisnet.nl
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

from meresco.components.statistics import log
from handlerequestfilter import HandleRequestFilter

class PathFilter(HandleRequestFilter):
    log = log

    def __init__(self, subPaths, excluding=[]):
        HandleRequestFilter.__init__(self, self._filter)
        self._subPaths = subPaths
        if type(subPaths) == str:
            self._subPaths = [subPaths]
        self._excluding = excluding

    def _filter(self, path, **kwargs):
        matchesSubPath = [subPath for subPath in self._subPaths if path.startswith(subPath)]
        matchesExcludedPath = [excludedPath for excludedPath in self._excluding if path.startswith(excludedPath)]
        if matchesSubPath and not matchesExcludedPath:
            self.log(path=matchesSubPath[0])
            return True
        return False
