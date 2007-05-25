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

from observers.oailistrecords import OaiListRecords, BATCH_SIZE
from cq2utils.calltrace import CallTrace
from observers.oai.	oaitool import resumptionTokenFromString, ResumptionToken
from amara.binderytools import bind_string

class OaiListRecordsTest(OaiTestCase):
	def getSubject(self):
		return OaiListRecords()
	
	def testNoArguments(self):
		self.assertBadArgument({'verb': ['ListRecords']}, 'Missing argument "resumptionToken" or "metadataPrefix"')
		
	def testTokenNotUsedExclusively(self):
		self.assertBadArgument({'verb': ['ListRecords'], 'resumptionToken': ['aToken'], 'from': ['aDate']}, '"resumptionToken" argument may only be used exclusively.')

	def testNeitherTokenNorMetadataPrefix(self):
		self.assertBadArgument({'verb': ['ListRecords'], 'from': ['aDate']}, 'Missing argument "resumptionToken" or "metadataPrefix"')

	def testNonsenseArguments(self):
		self.assertBadArgument({'verb': ['ListRecords'], 'metadataPrefix': ['aDate'], 'nonsense': ['more nonsense'], 'bla': ['b']}, 'Argument(s) "bla", "nonsense" is/are illegal.')

	def testDoubleArguments(self):
		self.assertBadArgument({'verb':['ListRecords'], 'metadataPrefix': ['oai_dc', '2']}, 'Argument "metadataPrefix" may not be repeated.')
	
	def testListRecordsUsingMetadataPrefix(self):
		self.request.args = {'verb':['ListRecords'], 'metadataPrefix': ['oai_dc']}
		
		class Observer:
			def listRecords(sself, continueAt = '0'):
				self.assertEquals('0', continueAt)
				return ['id_0', 'id_1']
					
			def write(sself, sink, id, partName):
				if partName == 'oai_dc':
					sink.write('<some:recorddata xmlns:some="http://some.example.org" id="%s"/>' % id)
				elif partName == '__internal__':
					sink.write("""<__internal__>
			<datestamp>DATESTAMP_FOR_TEST</datestamp>
			<unique>UNIQUE_NOT_USED_YET</unique>
		</__internal__>""")
				else:
					self.fail(partName + ' is unexpected')
			
			def undo(sself, *args, **kwargs):
				pass
			def notify(sself, *args, **kwargs):
				pass
		
		self.subject.addObserver(Observer())
		self.observable.changed(self.request)
		
		self.assertEqualsWS(self.OAIPMH % """
<request metadataPrefix="oai_dc"
 verb="ListRecords">http://server:9000/path/to/oai</request>
 <ListRecords>
   <record> 
    <header>
      <identifier>id_0</identifier> 
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
    <metadata>
      <some:recorddata xmlns:some="http://some.example.org" id="id_0"/>
    </metadata>
   </record>
   <record> 
    <header>
      <identifier>id_1</identifier> 
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
    <metadata>
      <some:recorddata xmlns:some="http://some.example.org" id="id_1"/>
    </metadata>
   </record>
 </ListRecords>""", self.stream.getvalue())
 
 		self.assertTrue(self.stream.getvalue().find('<resumptionToken') == -1)
	
	def testListRecordsUsingToken(self):
		self.request.args = {'verb':['ListRecords'], 'resumptionToken': [str(ResumptionToken('oai_dc', '10'))]}
		
		observer = CallTrace('RecordAnswering')
		def listRecords(continueAt = '0'):
			self.assertEquals('10', continueAt)
			return []
				
		observer.listRecords = listRecords
		self.subject.addObserver(observer)
		self.observable.changed(self.request)
		
	def testResumptionTokensAreProduced(self):
		self.request.args = {'verb':['ListRecords'], 'metadataPrefix': ['oai_dc']}
		observer = CallTrace('RecordAnswering')
		def listRecords(continueAt = '0'):
			return map(lambda i: 'id_%i' % i, range(1000))
				
		def write(sink, id, partName):
			if partName == 'oai_dc':
				pass
			elif partName == '__internal__':
				sink.write("""<__internal__>
		<datestamp>DATESTAMP_FOR_TEST</datestamp>
		<unique>666</unique>
	</__internal__>""")
		observer.listRecords = listRecords
		observer.write = write
		self.subject.addObserver(observer)
		
		self.observable.changed(self.request)
		
		self.assertTrue(self.stream.getvalue().find("<resumptionToken>") > -1)
		xml = bind_string(self.stream.getvalue()).OAI_PMH.ListRecords.resumptionToken
		resumptionToken = resumptionTokenFromString(str(xml))
		self.assertEquals('666', resumptionToken._continueAt)
		self.assertEquals('oai_dc', resumptionToken._metadataPrefix)
			
	def testFinalResumptionToken(self):
		self.request.args = {'verb':['ListRecords'], 'resumptionToken': [str(ResumptionToken('oai_dc', '200'))]}
		observer = CallTrace('RecordAnswering')
		def listRecords(continueAt = '0'):
			return map(lambda i: 'id_%i' % i, range(BATCH_SIZE))
		def write(sink, id, partName):
			if partName == '__internal__':
				sink.write("""<__internal__>
		<datestamp>DATESTAMP_FOR_TEST</datestamp>
		<unique>666</unique>
	</__internal__>""")
		observer.listRecords = listRecords
		observer.write = write
		self.subject.addObserver(observer)
		
		self.observable.changed(self.request)
		
		self.assertTrue(self.stream.getvalue().find("resumptionToken") > -1)
		self.assertEquals('', str(bind_string(self.stream.getvalue()).OAI_PMH.ListRecords.resumptionToken))
	