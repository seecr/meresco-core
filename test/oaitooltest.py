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

from meresco.queryserver.observers.oai.oaitool import ResumptionToken, resumptionTokenFromString, ISO8601Exception, ISO8601
from cq2utils.cq2testcase import CQ2TestCase

class OaiToolTest(CQ2TestCase):
	
	def assertResumptionToken(self, token):
		aTokenString = str(token)
		token2 = resumptionTokenFromString(aTokenString)
		self.assertEquals(token, token2)
	
	def testResumptionToken(self):
		self.assertResumptionToken(ResumptionToken())
		self.assertResumptionToken(ResumptionToken('oai:dc', '100', '2002-06-01T19:20:30Z', '2002-06-01T19:20:39Z', 'some:set:name'))
		
	def testISO8601(self):
		"""http://www.w3.org/TR/NOTE-datetime
   Below is the complete spec by w3. OAI-PMH only allows for 
   YYYY-MM-DD and
   YYYY-MM-DDThh:mm:ssZ
   
   Year:
      YYYY (eg 1997)
   Year and month:
      YYYY-MM (eg 1997-07)
   Complete date:
      YYYY-MM-DD (eg 1997-07-16)
   Complete date plus hours and minutes:
      YYYY-MM-DDThh:mmTZD (eg 1997-07-16T19:20+01:00)
   Complete date plus hours, minutes and seconds:
      YYYY-MM-DDThh:mm:ssTZD (eg 1997-07-16T19:20:30+01:00)
   Complete date plus hours, minutes, seconds and a decimal fraction of a
second
      YYYY-MM-DDThh:mm:ss.sTZD (eg 1997-07-16T19:20:30.45+01:00)"""
		
		def right(s):
			ISO8601(s)
		
		def wrong(s):
			try:
				ISO8601(s)
				self.fail()
			except ISO8601Exception, e:
				pass
			
		wrong('2000')
		wrong('2000-01')
		right('2000-01-01')
		wrong('aaaa-bb-cc')
		wrong('2000-01-32')
		wrong('2000-01-01T00:00Z')
		right('2000-01-01T00:00:00Z')
		right('2000-12-31T23:59:59Z')
		wrong('2000-01-01T00:00:61Z')
		wrong('2000-01-01T00:00:00+01:00')
		wrong('2000-01-01T00:00:00.000Z')
		
		iso8601 = ISO8601('2000-01-01T00:00:00Z')
		self.assertFalse(iso8601.isShort())
		self.assertEquals('2000-01-01T00:00:00Z', str(iso8601))
		self.assertEquals('2000-01-01T00:00:00Z', iso8601.floor())
		self.assertEquals('2000-01-01T00:00:00Z', iso8601.ceil())
		
		iso8601 = ISO8601('2000-01-01')
		self.assertTrue(iso8601.isShort())
		self.assertEquals('2000-01-01T00:00:00Z', str(iso8601))
		self.assertEquals('2000-01-01T00:00:00Z', iso8601.floor())
		self.assertEquals('2000-01-01T23:59:59Z', iso8601.ceil())
