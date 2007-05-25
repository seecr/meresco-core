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

from oaitestcase import OaiTestCase

from observers.oaiidentify import OaiIdentify
from observers.oai.oaivalidator import assertValidString

class OaiIdentifyTest(OaiTestCase):
	def getSubject(self):
		return OaiIdentify()
	
	def testIdentify(self):
		self.request.args = {'verb': ['Identify']}
		
		self.observable.changed(self.request)
		
		self.assertEquals("setHeader('content-type', 'text/xml; charset=utf-8')",  str(self.request.calledMethods[0]))
		self.assertEqualsWS(self.OAIPMH % """
		<request verb="Identify">http://server:9000/path/to/oai</request>
<Identify>
    <repositoryName>The Repository Name</repositoryName>
    <baseURL>http://server:9000/path/to/oai</baseURL>
    <protocolVersion>2.0</protocolVersion>
    <adminEmail>info@cq2.nl</adminEmail>
    <earliestDatestamp>1970-01-01T00:00:00Z</earliestDatestamp>
    <deletedRecord>no</deletedRecord>
    <granularity>YYYY-MM-DDThh:mm:ssZ</granularity>
  </Identify>""", self.stream.getvalue())
		assertValidString(self.stream.getvalue())
		
	def testIllegalArguments(self):
		self.assertBadArgument({'verb': ['Identify'], 'metadataPrefix': ['oai_dc']}, 'Identify verb must be single argument.')		