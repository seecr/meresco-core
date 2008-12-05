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

from cq2utils.cq2testcase import CQ2TestCase

from meresco.components.storagecomponent import StorageComponent
from storage import HierarchicalStorage, Storage
from cStringIO import StringIO
from meresco.framework.observable import Observable

class StorageComponentTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.storageComponent = StorageComponent(self.tempdir, revisionControl=True)
        self.storage = self.storageComponent._storage

    def testAdd(self):
        old,new = self.storageComponent.add("id_0", "partName", "The contents of the part")
        self.assertEquals('The contents of the part', self.storage.get(('id_0', 'partName')).read())
        self.assertEquals((0,1), (old,new))

    def testIsAvailableIdAndPart(self):
        sink = self.storage.put(('some:thing:anId-123','somePartName'))
        sink.send('read string')
        sink.close()

        hasId, hasPartName = self.storageComponent.isAvailable("some:thing:anId-123", "somePartName")
        self.assertTrue(hasId)
        self.assertTrue(hasPartName)

    def testIsAvailableId(self):
        sink = self.storage.put(('some:thing:anId-123','somePartName.xml'))
        sink.send('read string')
        sink.close()

        hasId, hasPartName = self.storageComponent.isAvailable("some:thing:anId-123", "nonExistingPart")
        self.assertTrue(hasId)
        self.assertFalse(hasPartName)

    def testIsNotAvailable(self):
        hasId, hasPartName = self.storageComponent.isAvailable("some:thing:anId-123", "nonExistingPart")
        self.assertFalse(hasId)
        self.assertFalse(hasPartName)

    def testWrite(self):
        sink = self.storage.put(('some:thing:anId-123','somePartName'))
        sink.send('read string')
        sink.close()
        stream = StringIO()
        self.storageComponent.write(stream, "some:thing:anId-123", "somePartName")
        self.assertEquals('read string', stream.getvalue())

    def testDeleteParts(self):
        identifier = ('some:thing:anId-123','somePartName')
        self.storage.put(identifier).close()
        self.assertTrue(identifier in self.storage)
        self.storageComponent.deletePart('some:thing:anId-123', 'somePartName')
        self.assertFalse(identifier in self.storage)

    def testDelete(self):
        identifier = ('some:thing:anId-123','somePartName')
        self.storage.put(identifier).close()
        self.assertTrue(identifier in self.storage)
        self.storageComponent.delete('some:thing:anId-123')
        self.assertTrue(identifier in self.storage)

        self.storageComponent = StorageComponent(self.tempdir, revisionControl=True, partsRemovedOnDelete=['somePartName'])
        self.storage = self.storageComponent._storage
        self.storageComponent.delete('some:thing:anId-123')
        self.assertFalse(identifier in self.storage)


    def testDeleteNonexisting(self):
        identifier = ('some:thing:anId-123','somePartName.xml')
        self.assertFalse(identifier in self.storage)
        self.storageComponent.deletePart('some:thing:anId-123', 'somePartName')
        self.assertFalse(identifier in self.storage)

    def testEnumerate(self):
        self.assertEquals([], list(self.storageComponent.listIdentifiers()))
        self.storageComponent.add('some:thing:anId-123','somePartName', 'data')
        self.assertEquals(['some:thing:anId-123'], list(self.storageComponent.listIdentifiers()))
        self.storageComponent.add('some:thing:anId-123','anotherPartName', 'data')
        self.assertEquals(['some:thing:anId-123'], list(self.storageComponent.listIdentifiers()))
        self.storageComponent.add('some:thing:anId-122','anotherPartName', 'data')
        self.assertEquals(['some:thing:anId-123', 'some:thing:anId-122'], list(self.storageComponent.listIdentifiers()))
