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
from meresco.components.storagecomponent import defaultSplit

from storage import HierarchicalStorage, Storage

from cStringIO import StringIO

def defaultJoin(parts):
    id = ":".join(parts[:-1])
    partName = parts[-1][:-1 * len('.xml')]
    return id, partName

class StorageHarvester(Observable):

    def __init__(self, storeDirectory, split=defaultSplit, join=defaultJoin):
        Observable.__init__(self)
        self._storage = HierarchicalStorage(Storage(storeDirectory), split=split , join=join)

    def main(self):
        for id, partName in self._storage:
            file = self._storage.get((id, partName))
            buffer = StringIO()
            for data in file:
                buffer.write(data)
            self.do.add(id, partName, buffer.getvalue())
            #KvS?TJ: het is natuurlijk jammer dat we hier getvalue aanroepen -idealiter is het framework stream-gebaseerd, niet  string-gebaseerd
