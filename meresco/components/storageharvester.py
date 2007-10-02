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

from meresco.framework.observable import Observable
from meresco.components.storagecomponent import defaultSplit

def defaultJoin(parts):
    id = ":".join(parts[:-1])
    partName = parts[-1][:-1 * len('.xml')]
    return id, partName

class StorageHarvester(Observable):

    def __init__(self, storagedir, split=defaultSplit, join=defaultJoin):
        Observable.__init__(self)
        self._storage = HierarchicalStorage(Storage(storeDirectory), split=split , join=join)
        for id, partName in self._storage:
            file = self._storage.get((id, partName))
            f = open(file.path)
            s = ''
            for data in file:
                s.append(data)
            self.do.add(id, partName, s)
