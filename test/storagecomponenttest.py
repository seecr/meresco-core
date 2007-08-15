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

from cq2utils.cq2testcase import CQ2TestCase

from meresco.components.storagecomponent import StorageComponent
from storage import HierarchicalStorage, Storage
from cq2utils.component import Notification
from cStringIO import StringIO
from meresco.framework.observable import Observable
 
class StorageComponentTest(CQ2TestCase):
            
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.storageComponent = StorageComponent(self.tempdir)
        self.storage = HierarchicalStorage(Storage(self.tempdir), split = lambda x:x)
    
    def testAdd(self):
        old,new = self.storageComponent.add("id_0", "partName", "The contents of the part")

        self.assertEquals('The contents of the part', self.storage.get(('id_0', 'partName.xml')).read())
        self.assertEquals((0,1), (old,new))

    def testIsAvailableIdAndPart(self):
        sink = self.storage.put(('some','thing:anId-123','somePartName.xml'))
        sink.send('read string')
        sink.close()
        
        hasId, hasPartName = self.storageComponent.isAvailable("some:thing:anId-123", "somePartName")
        self.assertTrue(hasId)
        self.assertTrue(hasPartName)
    
    def testIsAvailableId(self):
        sink = self.storage.put(('some','thing:anId-123','somePartName.xml'))
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
        sink = self.storage.put(('some','thing:anId-123','somePartName.xml'))
        sink.send('read string')
        sink.close()
        
        stream = StringIO()
        self.storageComponent.write(stream, "some:thing:anId-123", "somePartName")
        self.assertEquals('read string', stream.getvalue())

    def testDelete(self):
        identifier = ('some','thing:anId-123','somePartName.xml')
        self.storage.put(identifier).close()
        self.assertTrue(identifier in self.storage)
        self.storageComponent.deletePart('some:thing:anId-123', 'somePartName')
        self.assertFalse(identifier in self.storage)

    def testDeleteNonexisting(self):
        identifier = ('some','thing:anId-123','somePartName.xml')
        self.assertFalse(identifier in self.storage)
        self.storageComponent.deletePart('some:thing:anId-123', 'somePartName')
        self.assertFalse(identifier in self.storage)
    