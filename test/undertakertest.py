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

from unittest import TestCase
from meresco.queryserver.observers.undertaker import Undertaker
from cq2utils.component import Notification
from amara.binderytools import bind_string

class UnderTakerTest(TestCase):
	
	def setUp(self):
		self.undertaker = Undertaker()
		self.undertaker.addObserver(self)
		self.notifyCalls = []
		self.deletedParts = []
	
	def testAdd(self):
		notification = Notification('add', 'AN_ID', 'A_PARTNAME', 'A PAYLOAD (is in reality amary object)')
		self.undertaker.notify(notification)
		self.assertEquals([(notification,)], self.notifyCalls)
		self.assertEquals([('AN_ID', '__tombstone__')], self.deletedParts)
		
	def testDelete(self):
		xml = bind_string("<__tombstone__/>").__tombstone__
		notification = Notification('delete', 'AN_ID')
		self.undertaker.notify(notification)
		self.assertEquals(map(str, [
			(notification,),
			(Notification('add', 'AN_ID', '__tombstone__', xml),)]), map(str, self.notifyCalls))
		
	def notify(self, *args):
		"""self shunt"""
		self.notifyCalls.append(args)
		
	def deletePart(self, id, partName):
		self.deletedParts.append((id, partName))
