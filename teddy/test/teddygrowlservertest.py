## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import unittest
import teddygrowlserver
from amara import binderytools

DOCUMENT = """<document id="anId_1">%s</document>"""

XML_PART = """<part name="part_1" type="text/xml">%s</part>
"""

TEXT_PART = """<part name="part_2" type="text/plain">Containing plain text</part>
"""

class TeddyGrowlServerTest(unittest.TestCase):
	
	def setUp(self):
		self.server = teddygrowlserver.TeddyGrowlServer(None)
		self.server.changed = self.notify
		self.notifications = []
	
	def testAdd(self):
		contents = """<someXML>text and<tag with="anAttribute"/>and more text</someXML>"""
		aDocument = binderytools.bind_string(DOCUMENT % XML_PART % contents).document
		self.server._processDocument(aDocument)
		
		self.assertEquals(1, len(self.notifications))
		self.assertEquals("add", self.notifications[0].method)
		self.assertEquals("anId_1", self.notifications[0].id)
		self.assertEquals("part_1", self.notifications[0].partName)
		self.assertEquals(contents, self.notifications[0].payload)
	
	def testAddTwoParts(self):
		aDocument = binderytools.bind_string(DOCUMENT % (
			(XML_PART % "<xml/>") +
			(TEXT_PART))).document
		self.server._processDocument(aDocument)
		
		self.assertEquals(2, len(self.notifications))
		self.assertEquals("add", self.notifications[0].method)
		self.assertEquals("anId_1", self.notifications[0].id)
		self.assertEquals("part_1", self.notifications[0].partName)
		self.assertEquals("<xml/>", self.notifications[0].payload)
		
		self.assertEquals("add", self.notifications[1].method)
		self.assertEquals("anId_1", self.notifications[1].id)
		self.assertEquals("part_2", self.notifications[1].partName)
		self.assertEquals("Containing plain text", self.notifications[1].payload)
	
	def testDelete(self):
		aDocument = binderytools.bind_string("""<document id="anId_1" delete="true"/>""").document
		
		self.server._processDocument(aDocument)
		
		self.assertEquals(1, len(self.notifications))
		self.assertEquals("delete", self.notifications[0].method)
		self.assertEquals("anId_1", self.notifications[0].id)
	
	def testObservable(self):
		server = teddygrowlserver.TeddyGrowlServer(None)
		server.addObserver(self)
		server.changed("a notification")
		self.assertEquals(["a notification"], self.notifications)
	
	def notify(self, notification):
		"""self shunt"""
		self.notifications.append(notification)
		
	def undo(self, *args, **kwargs):
		"""self shunt"""
		pass
