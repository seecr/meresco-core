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
from cq2utils.calltrace import CallTrace

from plugins.resetplugin import ResetPlugin, registerOn
from cStringIO import StringIO

class ResetPluginTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.stream = StringIO()
		self.request = CallTrace('Request')
		client = CallTrace('client')
		self.request.client = client
		client.host = '127.0.0.1'
		self.request.write = self.stream.write
		self.request.args = {}
		self.request.database = 'database'
		self.searchInterface = CallTrace('SearchInterface')
		self.plugin = ResetPlugin(self.request, self.searchInterface)
	
	def testRegistry(self):
		registry = CallTrace('PluginRegistry')
		registerOn(registry)
		self.assertEquals(1, len(registry.calledMethods))
		self.assertEquals("registerByCommand('reset', <class plugins.resetplugin.ResetPlugin>)", str(registry.calledMethods[0]))
		
	def testReset(self):
		self.plugin.process()
		self.assertEquals(1, len(self.searchInterface.calledMethods))
		self.assertEquals("reset()", str(self.searchInterface.calledMethods[0]))
		self.assertEqualsWS('Done', self.stream.getvalue())
		
	def testExternalReset(self):
		self.request.client.host = '1.1.1.1'
		self.plugin.process()
		self.assertEquals(0, len(self.searchInterface.calledMethods))
		self.assertEqualsWS('Not authorized', self.stream.getvalue())
		
