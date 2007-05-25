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

from storagecomponent import StorageComponent
from cq2utils.component import Notification
from cStringIO import StringIO
from cq2utils.observable import Observable
 
class StorageComponentTest(CQ2TestCase):
			
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.storageComponent = StorageComponent(self)
		self.removedUnit = None
		self.gottenUnit = None
		self.openedBox = None
		self.written = None
		
		self.notification = Notification()
		self.notification.method = "add"
		self.notification.id = "anId-123"
		self.notification.partName = "somePartName"
		self.notification.payload = "The contents of the part"
		
		self.observable = Observable()
		self.observable.addObserver(self.storageComponent)
	
	def testAdd(self):
		self.observable.changed(self.notification)
		
		self.assertEquals(None, self.removedUnit)
		self.assertEquals("anId-123", self.gottenUnit)
		self.assertEquals("somePartName", self.openedBox)
		self.assertEquals("The contents of the part", self.written)

	def testIsAvailable(self):
		hasId, hasPartName = self.storageComponent.isAvailable("anId-123", "somePartName")
		
		self.assertTrue(hasId)
		self.assertTrue(hasPartName)
		
	def testWrite(self):
		self.storageComponent.write(self, "anId-123", "somePartName")
		self.assertEquals('read string', self.written)
	
	def hasUnit(self, anId):
		"""Storage shunt"""
		return True
	
	def removeUnit(self, anId):
		"""Storage shunt"""
		self.removedUnit = anId
	
	def getUnit(self, anId):
		"""Storage shunt"""
		self.gottenUnit = anId
		return self
	
	def hasBox(self, boxName):
		"""Unit shunt"""
		return True
	
	def openBox(self, boxName, mode = 'r'):
		"""Unit shunt"""
		self.openedBox = boxName
		return self

	def write(self, string):
		"""Stream shunt"""
		self.written = string
		
	def read(self):
		return 'read string'
		
	def close(self):
		"""Stream shunt"""
		pass
