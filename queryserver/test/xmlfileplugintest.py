## begin license ##
#
#    QueryServer is a framework for handling search queries.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of QueryServer.
#
#    QueryServer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    QueryServer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QueryServer; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from unittest import TestCase
from plugins.xmlfileplugin import XMLFilePlugin, FILE_PATH, registerOn
from pluginregistry import PluginRegistry
from cq2utils.calltrace import CallTrace
from tempfile import mkdtemp
from shutil import rmtree

import tempfile, os

class XMLFilePluginTest(TestCase):
	def createPlugin(self, request, configuration):
		command = 'xsd'
		request.configuration = configuration
		request.args = {}
		request.serverurl = "http://example.org/xsd" 
		request.getenv = lambda key: configuration[key]
		request.database = 'database'
		return self.registry.create(command, request, self.searchInterface)
	
	def setUp(self):
		self._writtenFiles = []
		self.registry = PluginRegistry({})
		registerOn(self.registry)
		self.searchInterface = None
		
	def tearDown(self):
		for file in self._writtenFiles:
			os.remove(file)
		
	def writeFile(self, contents):
		fd, filename = tempfile.mkstemp()
		f = open(filename, 'w')
		try:
			f.write(contents)
		finally:
			f.close()
			
		xsdPath = os.path.dirname(filename)
		xsdName = os.path.basename(filename)
		self._writtenFiles.append(filename)
		
		return xsdPath, xsdName
		
	def testContentType(self):
		configuration = {FILE_PATH:'/tmp'}
		plugin = self.createPlugin(CallTrace('Request'), configuration)
		self.assertEquals('text/xml; charset=utf-8', plugin.contentType)
		
	def testNonexistingXSD(self):
		configuration = {FILE_PATH:'/tmp'}
		plugin = self.createPlugin(CallTrace('Request'), configuration)
		result = plugin.getContents('NoneExisting')
		self.assertEquals('', result)
		
	def testServeFile(self):
		contents = 'xsd file contents'
			
		xsdPath, xsdName = self.writeFile(contents)	
		configuration = {FILE_PATH:xsdPath}
		plugin = self.createPlugin(CallTrace('Request'), configuration)
		result = plugin.getContents(xsdName)
		self.assertEquals(contents, result)
		
	def testProcess(self):
		contents = 'xsd file contents'
		xsdPath, xsdName = self.writeFile(contents)
		
		request = CallTrace('request')
		request.path = '/xsd/' + xsdName
		
		configuration = {FILE_PATH:xsdPath}
		plugin = self.createPlugin(request, configuration)
		plugin.process()
		
		self.assertEquals(3, len(request.calledMethods), request.calledMethods)
		self.assertEquals("setResponseCode(200)", str(request.calledMethods[0]))
		self.assertEquals("setHeader('content-type', 'text/xml; charset=utf-8')", str(request.calledMethods[1]))
		self.assertEquals("write('xsd file contents')", str(request.calledMethods[2]))
		
	def testWsdlPlugin(self):
		command = 'wsdl'
		request = CallTrace('request')
		request.path = '/database/wsdl'
		request.database = 'database'
		request.args = {}
		tmpdir = mkdtemp()
		try:
			f = file(tmpdir + '/srw.wsdl', 'w')
			f.write('SRW')
			f.close()
			request.configuration = {FILE_PATH:tmpdir}
			request.getenv = request.configuration.get
			
			plugin = self.registry.create(command, request, self.searchInterface)
			
			plugin.process()
			
			self.assertEquals(3, len(request.calledMethods), request.calledMethods)
			self.assertEquals("setResponseCode(200)", str(request.calledMethods[0]))
			self.assertEquals("setHeader('content-type', 'text/xml; charset=utf-8')", str(request.calledMethods[1]))
			self.assertEquals("write('SRW')", str(request.calledMethods[2]))
		finally:
			rmtree(tmpdir)

	
