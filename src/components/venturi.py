## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
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

from cq2utils.component import Component, Notification
from meresco.framework.observable import Observable
from amara import binderytools


class Venturi(Component, Observable):
    """
    Will create a new or update an existing document with a notification
    """
    def __init__(self, venturiName, storage):
        Observable.__init__(self)
        self._storage = storage
        self._venturiName = venturiName

    def add(self, id, name, newNode):
        unit = self._storage.getUnit(id)
        if unit.hasBox(self._venturiName):
            box = unit.openBox(self._venturiName)
            try:
                venturiObject = binderytools.bind_stream(box).rootNode.childNodes[0]
                existingNode = getattr(venturiObject, newNode.localName, None)
                if existingNode:
                    venturiObject.xml_remove_child(existingNode)
            finally:
                box.close()
        else:
            venturiObject = binderytools.bind_string('<%s/>' % self._venturiName).rootNode.childNodes[0]
        venturiObject.xml_append(newNode)
        return self.all.add(id, self._venturiName, venturiObject)
