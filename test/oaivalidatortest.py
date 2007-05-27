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

from meresco.queryserver.observers.oai.oaivalidator import assertValidString, validate
from cStringIO import StringIO

class OaiValidatorTest(CQ2TestCase):
	def testAssertValidString(self):
		s = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
<responseDate>2007-01-01T00:00:00Z</responseDate>
<request verb="Identify">url</request>
<Identify>
    <repositoryName>The Repository Name</repositoryName>
    <baseURL>http://base.example.org/url</baseURL>
    <protocolVersion>2.0</protocolVersion>
    <adminEmail>info@cq2.nl</adminEmail>
    <earliestDatestamp>1970-01-01T00:00:00Z</earliestDatestamp>
    <deletedRecord>no</deletedRecord>
    <granularity>YYYY-MM-DDThh:mm:ssZ</granularity>
  </Identify>
</OAI-PMH>"""
		assertValidString(s)
		success, message = validate(StringIO(s))
		self.assertEquals(True, success)
		self.assertEquals('', message)
		
	def testAssertInvalidString(self):
		raisedError = None
		try:
			assertValidString('<OAI-PMH/>')
			raisedError = False
		except AssertionError, e:
			raisedError = True
			message = str(e)
		self.assertEquals(True, raisedError)
		self.assertEqualsWS("<string>:1:ERROR:SCHEMASV:SCHEMAV_CVC_ELT_1: Element 'OAI-PMH': No matching global declaration available for the validation root.", message)
