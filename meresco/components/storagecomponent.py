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

from storage import HierarchicalStorage, Storage
from itertools import ifilter

def defaultSplit((id, partName)):
    result = id.split(':',1)
    if partName != None:
        result += [partName]
    return result

def defaultJoin(parts):
    id = ":".join(parts[:-1])
    partName = parts[-1]
    return id, partName

class StorageComponent(object):
    def __init__(self, directory, split=defaultSplit, join=defaultJoin, revisionControl=False, partsRemovedOnDelete=[]):
        assert type(directory) == str, 'Please use directory as first parameter'
        self._storage = HierarchicalStorage(Storage(directory, revisionControl=revisionControl, ), split, join)
        self._partsRemovedOnDelete = partsRemovedOnDelete

    def store(self, *args, **kwargs):
        return self.add(*args, **kwargs)

    def add(self, id, partName, someString, *args, **kwargs):
        sink = self._storage.put((id, partName))
        try:
            sink.send(someString)
        finally:
            return sink.close()

    def delete(self, id):
        for partName in self._partsRemovedOnDelete:
            self.deletePart(id, partName)

    def deletePart(self, id, partName):
        if (id, partName) in self._storage:
            self._storage.delete((id, partName))

    def isAvailable(self, id, partName):
        """returns (hasId, hasPartName)"""
        if (id, partName) in self._storage:
            return True, True
        elif (id, None) in self._storage:
            return True, False
        return False, False

    def write(self, sink, id, partName):
        stream = self._storage.get((id, partName))
        try:
            for line in stream:
                sink.write(line)
        finally:
            stream.close()

    def yieldRecord(self, id, partName):
        stream = self._storage.get((id, partName))
        for data in stream:
            yield data
        stream.close()

    def getStream(self, id, partName):
        return self._storage.get((id, partName))

    def _listIdentifiers(self):
        lastIdentifier = None
        for identifier, partname in self._storage:
            if identifier != lastIdentifier:
                yield identifier
                lastIdentifier = identifier

    def _listIdentifiersByPartName(self, partName):
        for identifier, partname in self._storage:
            if partName == partname:
                yield identifier

    def listIdentifiers(self, partName=None):
        """Use an ifilter to hide the generator so it won't be consumed by compose"""
        if partName:
            return ifilter(None, self._listIdentifiersByPartName(partName))
        return ifilter(None, self._listIdentifiers())
