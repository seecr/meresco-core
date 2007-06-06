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
import unittest
from meresco.teddy.srurecordupdateplugin import SRURecordUpdatePlugin
from StringIO import StringIO

XML = """<?xml version="1.0" encoding="UTF-8"?>
<updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="http://www.loc.gov/KVS_IHAVENOIDEA/">
	<srw:version>1.0</srw:version>
	<ucp:action>info:srw/action/1/%(action)s</ucp:action>
	<ucp:recordIdentifier>%(recordIdentifier)s</ucp:recordIdentifier>
	<srw:record>
		<srw:recordPacking>%(recordPacking)s</srw:recordPacking>
		<srw:recordSchema>%(recordSchema)s</srw:recordSchema>
		<srw:recordData>%(recordData)s</srw:recordData>
		%(hook)s
	</srw:record>	
</updateRequest>"""

XML_DOCUMENT = """<someXml>
with strings<nodes and="attributes"/>
</someXml>"""

TEXT_DOCUMENT = """Just some text"""

CREATE = "create"
REPLACE = "replace"
DELETE = "delete"

class SRURecordUpdatePluginTest(unittest.TestCase):
	"""http://www.loc.gov/standards/sru/record-update/"""
	
	def setUp(self):
		self.plugin = SRURecordUpdatePlugin()
		self.plugin.changed = self.pluginChanged
		self.notifications = []
		self.dictionary = {
			"action": CREATE,
			"recordIdentifier": "123",
			"recordPacking": "text/xml",
			"recordSchema": "irrelevantXML",
			"recordData": XML_DOCUMENT,
			"hook": ""}
			
	def notifyPlugin(self):
		content = XML % self.dictionary
		self.httpServerNotification = MockHTTPRequest(content)
		self.plugin.notify(self.httpServerNotification)
	
	def testAddXML(self):
		self.notifyPlugin()
		self.assertEquals(1, len(self.notifications))
		notification = self.notifications[0]
		self.assertEquals("add", notification.method)
		self.assertEquals("123", notification.id)
		self.assertEquals(str, type(notification.id))
		self.assertEquals("irrelevantXML", notification.partName)
		self.assertEquals(XML_DOCUMENT, notification.payload)
		
	def testExtraRecordData(self):
		self.dictionary["hook"] = "<srw:extraRecordData><one><a/></one><two/></srw:extraRecordData>"
		self.notifyPlugin()
		self.assertEquals(1, len(self.notifications))
		notification = self.notifications[0]
		self.assertEquals("<one><a/></one><two/>", notification.extraRecordData)
		
	def testSets(self):
		self.dictionary["hook"] = "<srw:extraRecordData><sets><set>one</set><set>two</set></sets></srw:extraRecordData>"
		self.notifyPlugin()
		self.assertEquals(1, len(self.notifications))
		notification = self.notifications[0]
		self.assertEquals(["one", "two"], notification.sets)
		
	def testAddText(self):
		self.dictionary["recordPacking"] = "text/plain"
		self.dictionary["recordData"] = TEXT_DOCUMENT
		self.notifyPlugin()
		self.assertEquals(1, len(self.notifications))
		notification = self.notifications[0]
		self.assertEquals(TEXT_DOCUMENT, notification.payload)
		
	def testDelete(self):
		self.dictionary["action"] = DELETE
		self.notifyPlugin()
		self.assertEquals(1, len(self.notifications))
		notification = self.notifications[0]
		self.assertEquals("delete", notification.method)
		
	def testReplaceIsAdd(self):
		self.dictionary["action"] = REPLACE
		self.notifyPlugin()
		self.assertEquals(1, len(self.notifications))
		notification = self.notifications[0]
		self.assertEquals("add", notification.method)
		
	def testResponse(self):
		self.notifyPlugin()
		self.assertTrue(self.httpServerNotification.written.find("""<ucp:operationStatus>succes</ucp:operationStatus>""") > -1)
		
	def testNotCorrectXml(self):
		httpServerNotification = MockHTTPRequest("nonsense")
		try:
			self.plugin.notify(httpServerNotification)
			self.fail()
		except Exception, e:
			self.assertEquals('SAXParseException', str(e.__class__).split('.')[-1])
		self.assertTrue(httpServerNotification.written.find("""<ucp:operationStatus>fail</ucp:operationStatus>""") > -1)
		
	def testErrorsArePassed(self):
		self.plugin.changed = self.pluginChangedThrowsException
		try:
			self.notifyPlugin()
			self.fail()
		except Exception, e:
			self.assertEquals('Shunted Exception', str(e))
		self.assertTrue(self.httpServerNotification.written.find("""<ucp:operationStatus>fail</ucp:operationStatus>""") > -1)
		self.assertTrue(self.httpServerNotification.written.find("""Shunted Exception""") > -1)
	
	def pluginChanged(self, notification):
		"""self shunt"""
		self.notifications.append(notification)
		
	def pluginChangedThrowsException(self, notification):
		"""self shunt"""
		self.notifications.append(notification)
		raise Exception("Shunted Exception")

class MockHTTPRequest:
	
	def __init__(self, content):
		self.content = StringIO(content)
		self.written = ""
		
	def write(self, s):
		self.written += s
