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
import meresco.queryserver.server
from meresco.queryserver.server import WebRequest
from meresco.queryserver.plugins.queryplugin import PluginException, QueryPlugin
from meresco.queryserver.pluginregistry import PluginRegistry

class ServerTest(unittest.TestCase):
	def setUp(self):
		self.written = ""
		self.transport = self
		channel = self
		self.configuration = {}
		self.registry = PluginRegistry({})
		self.searchInterfaces = {'database': None}
		self.request = WebRequest(self.configuration, self.registry, self.searchInterfaces, channel, None)
		self.request.finish = lambda : ''
		self.request.write = self.write
		self.contentType = 'text/plain'
		self.request.args = {}
		self.request.path = '/database/command'
		self.process_exception = None
		meresco.queryserver.server.log = lambda *args: None
		
	def testHandleBasicDefault(self):
		"""Test handle without a Plugin"""
		self.request.path = '/database/testHandleBasicDefault'
		self.request.process()
		self.assertEquals('<?xml version="1.0"?><error>Command "testHandleBasicDefault" not found.</error>', self.written)
		self.assertEquals(500, self.request.code)
		
	def register(self, processMethod, command):
		class MyPlugin(QueryPlugin):
			def initialize(self):
				pass
			def process(self):
				processMethod(self)
		self.registry.registerByCommand(command, MyPlugin)
		self.request.path = '/database/' + command
	
	
	def testHandleDefaultWithPlugin(self):
		"""Test handle with a Plugin"""
		def process(pluginSelf):
			pluginSelf.write('Process SUCCES')
		self.register(process, 'testHandleDefaultWithPlugin')
		self.request.process()
		self.assertEquals('Process SUCCES', self.written)
		self.assertEquals(200, self.request.code)
		
	def testHandleDefaultWithPluginAndError(self):
		"""Test handle with a Plugin creating error"""
		def raiseException(pluginSelf):
			raise PluginException('<?xml version="utf-8"?><bad/>')
		self.register(raiseException, 'testHandleDefaultWithPluginAndError')
		self.request.process()
		self.assertEquals('<?xml version="utf-8"?><bad/>', self.written)
		self.assertEquals(500, self.request.code)
			
	def assertPath(self, expectedDatabase, expectedCommand, path):
		self.request.path = path
		self.request._initializeRequestSettings()
		self.assertEquals(expectedDatabase, self.request.database)
		self.assertEquals(expectedCommand, self.request.command)
		
	def testDatabaseNotFound(self):
		def process(pluginSelf):
			pluginSelf.write('Process SUCCES')
		self.register(process, 'testDatabaseNotFound')
		self.request.path = '/nosuchdatabase/testDatabaseNotFound'
		self.request.process()
		self.assertEquals('400 Bad Request: database "nosuchdatabase" not found.', self.written)
		self.assertEquals(400, self.request.code)
		
		
	def testSplitPath(self):
		self.assertPath('x', "cmd", "/x/cmd")
		self.assertPath('x', "", "/x/")
		self.assertPath('', "", "/")
		self.assertPath('x', "cmd", "/x/cmd/whatever")
		
	def write(self, data):
		"""Shunt"""
		self.written += data
		
if __name__ == '__main__':
	unittest.main()
