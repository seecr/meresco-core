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

