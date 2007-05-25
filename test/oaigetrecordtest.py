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

from queryserver.observers.oaigetrecord import OaiGetRecord
from queryserver.observers.oai.oaivalidator import assertValidString
from cq2utils.calltrace import CallTrace

class OaiGetRecordTest(OaiTestCase):
	def getSubject(self):
		return OaiGetRecord()	
		
	def testGetRecordNoArguments(self):
		self.assertBadArgument({'verb': ['GetRecord']}, 'Missing argument(s) "identifier", "metadataPrefix".')
		
	def testGetNoMetadataPrefix(self):
		self.assertBadArgument({'verb': ['GetRecord'], 'identifier': ['oai:ident']}, 'Missing argument(s) "metadataPrefix".')

	def testGetNoIdentifierArgument(self):
		self.assertBadArgument({'verb': ['GetRecord'], 'metadataPrefix': ['oai_dc']}, 'Missing argument(s) "identifier".')

	def testNonsenseArgument(self):
		self.assertBadArgument({'verb': ['GetRecord'], 'metadataPrefix': ['aPrefix'], 'identifier': ['anIdentifier'], 'nonsense': ['bla']}, 'Argument(s) "nonsense" is/are illegal.')

	def testDoubleArguments(self):
		self.assertBadArgument({'verb':['GetRecord'], 'metadataPrefix': ['oai_dc'], 'identifier': ['oai:ident', '2']}, 'Argument "identifier" may not be repeated.')
	
	def testGetRecordNotAvailable(self):
		self.request.args = {'verb':['GetRecord'], 'metadataPrefix': ['oai_dc'], 'identifier': ['oai:ident']}
		
		observer = CallTrace('RecordAnswering')
		notifications = []
		def isAvailable(id, partName):
			notifications.append((id, partName))
			return False, False
		observer.isAvailable = isAvailable
		self.subject.addObserver(observer)
		
		self.observable.changed(self.request)
		
		self.assertEqualsWS(self.OAIPMH % """
<request>http://server:9000/path/to/oai</request>
<error code="idDoesNotExist">The value of the identifier argument is unknown or illegal in this repository.</error>""", self.stream.getvalue())
		assertValidString(self.stream.getvalue())
		
		self.assertEquals([('oai:ident', 'oai_dc')], notifications)
		
	def testGetRecord(self):
		self.request.args = {'verb':['GetRecord'], 'metadataPrefix': ['oai_dc'], 'identifier': ['oai:ident']}
		
		class Observable:
			def isAvailable(sself, id, partName):
				return True, True
			
			def write(sself, sink, id, partName):
				if partName == 'oai_dc':
					sink.write('<some:recorddata xmlns:some="http://some.example.org"/>')
				elif partName == '__internal__':
					sink.write("""<__internal__>
			<datestamp>DATESTAMP_FOR_TEST</datestamp>
			<unique>UNIQUE_NOT_USED_YET</unique>
		</__internal__>""")
			
			def undo(sself, *args, **kwargs):
				pass
			def notify(sself, *args, **kwargs):
				pass
			
		self.subject.addObserver(Observable())
		self.observable.changed(self.request)
		self.assertEqualsWS(self.OAIPMH % """
<request identifier="oai:ident"
 metadataPrefix="oai_dc"
 verb="GetRecord">http://server:9000/path/to/oai</request>
   <GetRecord>
   <record> 
    <header>
      <identifier>oai:ident</identifier> 
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
    <metadata>
      <some:recorddata xmlns:some="http://some.example.org"/>
    </metadata>
  </record>
 </GetRecord>""", self.stream.getvalue())
