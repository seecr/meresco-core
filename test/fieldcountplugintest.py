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

from queryserver.plugins.fieldcountplugin import FieldCountPlugin, registerOn, XML_CONTENT_TYPE, PluginException, ERROR_MESSAGE
from cq2utils.calltrace import CallTrace
from cStringIO import StringIO

class FieldCountPluginTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.stream = StringIO()
		self.request = CallTrace('Request')
		self.request.write = self.stream.write
		self.request.args = {}
		self.request.database = 'database'
		self.searchInterface = CallTrace('SearchInterface')
		self.plugin = FieldCountPlugin(self.request, self.searchInterface)
			
	def testRegistry(self):
		registry = CallTrace('PluginRegistry')
		registerOn(registry)
		self.assertEquals(1, len(registry.calledMethods))
		self.assertEquals("registerByCommand('fieldcount', <class queryserver.plugins.fieldcountplugin.FieldCountPlugin>)", str(registry.calledMethods[0]))
		
	def testFieldNotSpecified(self):
		try:
			self.plugin.process()
			self.fail()
		except PluginException, e:
			self.assertEquals(ERROR_MESSAGE % "field", str(e))
		
	def testSimple(self):
		self.searchInterface.returnValues['countField'] = [('a',1)]
		self.plugin._arguments = {'field':['dctype']}
	
		self.assertEquals(XML_CONTENT_TYPE, self.plugin.contentType)
		self.plugin.process()
		self.assertEquals(1, len(self.searchInterface.calledMethods), self.stream.getvalue())
		self.assertEquals("countField('dctype')", str(self.searchInterface.calledMethods[0]))
		self.assertEqualsWS(RESULT, self.stream.getvalue())
		
		
RESULT = """<?xml version="1.0" encoding="UTF-8"?>
<fieldcount count="1">
	<item>
		<value>a</value>
		<count>1</count>
	</item>
</fieldcount>
"""


