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

from meresco.framework.observable import Observable
from meresco.components.dictionary import DocumentField

import re

class Transform(Observable):
    def __init__(self, transformations):
        Observable.__init__(self)
        self._transformations = {}
        for source, target, transformer in transformations:
            if not source in self._transformations:
                self._transformations[source] = []
            self._transformations[source].append((target, transformer))

    def addField(self, id, documentField):
        self.do.addField(id, documentField)
        transformations = self._transformations.get(documentField.key, [])
        for target, transformer in transformations:
            for newValue in transformer(documentField.value):
                self.do.addField(id, DocumentField(target, newValue, **documentField.options))

class CleanSplit:
    def __init__(self, separator):
        self.separator = separator

    def __call__(self, s):
        return [part.strip() for part in s.split(self.separator)]

def years(s):
    yearRe = re.compile('\d{4}')
    return yearRe.findall(s)

