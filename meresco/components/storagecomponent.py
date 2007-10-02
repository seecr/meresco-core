## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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
from cq2utils.component import Component
from storage import HierarchicalStorage, Storage, HierarchicalStorageError

def defaultSplit((id, partName)):
    result = id.split(':',1)
    if partName != None:
        result += [partName + '.xml']
    return result

class StorageComponent(Component):
    def __init__(self, storeDirectory, split=defaultSplit):
        self._storage = HierarchicalStorage(Storage(storeDirectory), split=split)

    def store(self, *args, **kwargs):
        return self.add(*args, **kwargs)

    def add(self, id, partName, someString, *args, **kwargs):
        sink = self._storage.put((id, partName))
        try:
            sink.send(someString)
        finally:
            return sink.close()

    def deletePart(self, id, partName):
        try:
            self._storage.delete((id, partName))
        except HierarchicalStorageError, ignored:
            pass

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

    def getStream(self, id, partName):
        return self._storage.get((id, partName))
