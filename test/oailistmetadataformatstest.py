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

from oaitestcase import OaiTestCase

from meresco.queryserver.observers.oailistmetadataformats import OaiListMetadataFormats
from meresco.queryserver.observers.oai.oaivalidator import assertValidString

class OaiListMetadataFormatsTest(OaiTestCase):
	
	def getSubject(self):
		return OaiListMetadataFormats([
			("oai_dc", "http://www.openarchives.org/OAI/2.0/oai_dc.xsd", "http://www.openarchives.org/OAI/2.0/oai_dc/"),
			("olac", "http://www.language-archives.org/OLAC/olac-0.2.xsd", "http://www.language-archives.org/OLAC/0.2/")])
	
	def testListAllMetadataFormats(self):
		self.request.args = {'verb': ['ListMetadataFormats']}
		
		self.observable.changed(self.request)
		
		self.assertEqualsWS(self.OAIPMH % """
		<request verb="ListMetadataFormats">http://server:9000/path/to/oai</request>
  <ListMetadataFormats>
   <metadataFormat>
     <metadataPrefix>oai_dc</metadataPrefix>
     <schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd
       </schema>
     <metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/
       </metadataNamespace>
   </metadataFormat>
   <metadataFormat>
     <metadataPrefix>olac</metadataPrefix>
     <schema>http://www.language-archives.org/OLAC/olac-0.2.xsd</schema>
     <metadataNamespace>http://www.language-archives.org/OLAC/0.2/
      </metadataNamespace>
   </metadataFormat>
  </ListMetadataFormats>""", self.stream.getvalue())
		assertValidString(self.stream.getvalue())
		
	def testIllegalArguments(self):
		self.assertBadArgument({'verb': ['ListMetadataFormats'], 'somethingElse': ['illegal']})