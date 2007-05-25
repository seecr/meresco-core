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
import os
from queryplugin import QueryPlugin

FILE_PATH = 'xmlfile.filepath'

class XMLFilePlugin(QueryPlugin):
	def initialize(self):
		self._filePath = self.getenv(FILE_PATH)
		self.contentType = 'text/xml; charset=utf-8'

	#TODO: refactor to generator / stream like style.
	def getContents(self, aFilename):
		absoluteFilename = os.path.join(self._filePath, aFilename)
		if not os.path.isfile(absoluteFilename):
			return ''
		contents = open(absoluteFilename).read() % locals()
		return contents
	
	def _writeFileContents(self, filename):
		self.write(self.getContents(filename))
	
	def process(self):
		self._writeFileContents(self._request.path.split('/')[-1])
		
class WSDLPlugin(XMLFilePlugin):
	def process(self):
		self._writeFileContents('srw.wsdl')
		
def registerOn(aRegistry):
	aRegistry.registerByCommand('wsdl', WSDLPlugin)
	aRegistry.registerByCommand('xsd', XMLFilePlugin)


