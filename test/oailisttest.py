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

from queryserver.observers.oailist import OaiList, BATCH_SIZE
from cq2utils.calltrace import CallTrace
from queryserver.observers.oai.	oaitool import resumptionTokenFromString, ResumptionToken
from amara.binderytools import bind_string
from StringIO import StringIO

class OaiListTest(OaiTestCase):
	def getSubject(self):
		return OaiList(['oai_dc'])
	
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
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				self.assertEquals('oai_dc', partName)
				self.assertEquals('0', continueAt)
				return ['id_0&0', 'id_1&1']
					
			def write(sself, sink, id, partName):
				if partName == 'oai_dc':
					sink.write('<some:recorddata xmlns:some="http://some.example.org" id="%s"/>' % id.replace('&', '&amp;'))
				elif partName == '__stamp__':
					sink.write("""<__stamp__>
			<datestamp>DATESTAMP_FOR_TEST</datestamp>
		</__stamp__>""")
				else:
					self.fail(partName + ' is unexpected')
			
			def isAvailable(sself, id, partName):
				if partName == 'oai_dc':
					return True, True
				return True, False
			
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
      <identifier>id_0&amp;0</identifier> 
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
    <metadata>
      <some:recorddata xmlns:some="http://some.example.org" id="id_0&amp;0"/>
    </metadata>
   </record>
   <record> 
    <header>
      <identifier>id_1&amp;1</identifier> 
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
    <metadata>
      <some:recorddata xmlns:some="http://some.example.org" id="id_1&amp;1"/>
    </metadata>
   </record>
 </ListRecords>""", self.stream.getvalue())
 		self.assertTrue(self.stream.getvalue().find('<resumptionToken') == -1)
	
	def testListRecordsUsingToken(self):
		self.request.args = {'verb':['ListRecords'], 'resumptionToken': [str(ResumptionToken('oai_dc', '10', 'FROM', 'UNTIL', 'SET'))]}
		
		observer = CallTrace('RecordAnswering')
		def listRecords(partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
			self.assertEquals('oai_dc', partName)
			self.assertEquals('10', continueAt)
			self.assertEquals('FROM', oaiFrom)
			self.assertEquals('UNTIL', oaiUntil)
			self.assertEquals('SET', oaiSet)
			return []
				
		observer.listRecords = listRecords
		self.subject.addObserver(observer)
		self.observable.changed(self.request)
		
	def testResumptionTokensAreProduced(self):
		self.request.args = {'verb':['ListRecords'], 'metadataPrefix': ['oai_dc'], 'from': ['2000-01-01T00:00:00Z'], 'until': ['2000-12-31T00:00:00Z'], 'set': ['SET']}
		observer = CallTrace('RecordAnswering')
		def listRecords(partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
			return map(lambda i: 'id_%i' % i, range(1000))
				
		def write(sink, id, partName):
			if partName == 'oai_dc':
				pass
			elif partName == '__stamp__':
				sink.write("""<__stamp__>
		<datestamp>DATESTAMP_FOR_TEST</datestamp>
		<unique>UNIQUE_FOR_TEST</unique>
	</__stamp__>""")
		observer.listRecords = listRecords
		observer.write = write
		self.subject.addObserver(observer)
		
		self.observable.changed(self.request)
		
		self.assertTrue(self.stream.getvalue().find("<resumptionToken>") > -1)
		xml = bind_string(self.stream.getvalue()).OAI_PMH.ListRecords.resumptionToken
		resumptionToken = resumptionTokenFromString(str(xml))
		self.assertEquals('UNIQUE_FOR_TEST', resumptionToken._continueAt)
		self.assertEquals('oai_dc', resumptionToken._metadataPrefix)
		self.assertEquals('2000-01-01T00:00:00Z', resumptionToken._from)
		self.assertEquals('2000-12-31T00:00:00Z', resumptionToken._until)
		self.assertEquals('SET', resumptionToken._set)
			
	def testFinalResumptionToken(self):
		self.request.args = {'verb':['ListRecords'], 'resumptionToken': [str(ResumptionToken('oai_dc', '200'))]}
		observer = CallTrace('RecordAnswering')
		def listRecords(partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
			return map(lambda i: 'id_%i' % i, range(BATCH_SIZE))
		def write(sink, id, partName):
			if partName == '__stamp__':
				sink.write("""<__stamp__>
		<datestamp>DATESTAMP_FOR_TEST</datestamp>
	</__stamp__>""")
		observer.listRecords = listRecords
		observer.write = write
		self.subject.addObserver(observer)
		
		self.observable.changed(self.request)
		
		self.assertTrue(self.stream.getvalue().find("resumptionToken") > -1)
		self.assertEquals('', str(bind_string(self.stream.getvalue()).OAI_PMH.ListRecords.resumptionToken))
	
	def testDeteledTombstones(self):
		self.request.args = {'verb':['ListRecords'], 'metadataPrefix': ['oai_dc']}
		
		class Observer:
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				self.assertEquals('0', continueAt)
				return ['id_0', 'id_1']
					
			def write(sself, sink, id, partName):
				if partName == 'oai_dc':
					sink.write('<some:recorddata xmlns:some="http://some.example.org" id="%s"/>' % id)
				elif partName == '__stamp__':
					sink.write("""<__stamp__>
			<datestamp>DATESTAMP_FOR_TEST</datestamp>
		</__stamp__>""")
				else:
					self.fail(partName + ' is unexpected')
			
			def isAvailable(sself, id, partName):
				if partName == '__tombstone__' and id == 'id_1':
					return True, True
				return True, False
			
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
    <header status="deleted">
      <identifier>id_1</identifier> 
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
   </record>
 </ListRecords>""", self.stream.getvalue())
 
 		self.assertTrue(self.stream.getvalue().find('<resumptionToken') == -1)
		
	def testFromAndUntil(self):
		#ok, deze test wordt zo lang dat het haast wel lijkt of hier iets niet klopt.... KVS
		
		#helper methods:
		results = [None, None]
		class Observer:
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				results[0] = oaiFrom
				results[1] = oaiUntil
				return ['id_0', 'id_1']
			
			def write(sself, sink, id, partName):
				if partName == 'oai_dc':
					sink.write('<some:recorddata xmlns:some="http://some.example.org" id="%s"/>' % id)
				elif partName == '__stamp__':
					sink.write("""<__stamp__>
			<datestamp>DATESTAMP_FOR_TEST</datestamp>
		</__stamp__>""")
				else:
					self.fail(partName + ' is unexpected')
			
			def isAvailable(sself, id, partName):
				if partName == '__tombstone__' and id == 'id_1':
					return True, True
				return True, False
			
			def undo(self, *args):
				pass
			def notify(self, *args):
				pass
				
		self.subject.addObserver(Observer())
					
		def doIt(oaiFrom, oaiUntil):
			self.stream = StringIO()
			self.request.write = self.stream.write
			self.request.args = {'verb':['ListRecords'], 'metadataPrefix': ['oai_dc']}
			if oaiFrom:
				self.request.args['from'] = [oaiFrom]
			if oaiUntil:
				self.request.args['until'] = [oaiUntil]
			self.observable.changed(self.request)
			return results
		
		def right(oaiFrom, oaiUntil, expectedFrom = None, expectedUntil = None):
			expectedFrom = expectedFrom or oaiFrom
			expectedUntil = expectedUntil or oaiUntil
			resultingOaiFrom, resultingOaiUntil = doIt(oaiFrom, oaiUntil)
			self.assertEquals(expectedFrom, resultingOaiFrom)
			self.assertEquals(expectedUntil, resultingOaiUntil)
			self.assertTrue(not "<error" in self.stream.getvalue())
		
		def wrong(oaiFrom, oaiUntil):
			doIt(oaiFrom, oaiUntil)
			self.assertTrue("""<error code="badArgument">""" in self.stream.getvalue())
		
		#start reading here
		right(None, None)
		right('2000-01-01T00:00:00Z', '2000-01-01T00:00:00Z')
		right('2000-01-01', '2000-01-01', '2000-01-01T00:00:00Z', '2000-01-01T23:59:59Z')
		right(None, '2000-01-01T00:00:00Z')
		right('2000-01-01T00:00:00Z', None)
		wrong('thisIsNotEvenADateStamp', 'thisIsNotEvenADateStamp')
		wrong('2000-01-01T00:00:00Z', '2000-01-01')
		wrong('2000-01-01T00:00:00Z', '1999-01-01T00:00:00Z')
		
	def testListIdentifiers(self):
		self.request.args = {'verb':['ListIdentifiers'], 'metadataPrefix': ['oai_dc']}
		
		class Observer:
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				self.assertEquals('0', continueAt)
				return ['id_0']
					
			def write(sself, sink, id, partName):
				if partName == 'oai_dc':
					sink.write('<some:recorddata xmlns:some="http://some.example.org" id="%s"/>' % id)
				elif partName == '__stamp__':
					sink.write("""<__stamp__>
			<datestamp>DATESTAMP_FOR_TEST</datestamp>
		</__stamp__>""")
				else:
					self.fail(partName + ' is unexpected')
			
			def isAvailable(sself, id, partName):
				if partName == 'oai_dc':
					return True, True
				return True, False
			
			def undo(sself, *args, **kwargs):
				pass
			def notify(sself, *args, **kwargs):
				pass
		
		self.subject.addObserver(Observer())
		self.observable.changed(self.request)
		
		self.assertEqualsWS(self.OAIPMH % """
<request metadataPrefix="oai_dc"
 verb="ListIdentifiers">http://server:9000/path/to/oai</request>
 <ListIdentifiers>
   <record> 
    <header>
      <identifier>id_0</identifier> 
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
   </record>
 </ListIdentifiers>""", self.stream.getvalue())

	def testNoRecordsMatch(self):
		self.request.args = {'verb':['ListIdentifiers'], 'metadataPrefix': ['oai_dc']}
		
		class Observer:
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				return []
					
			def undo(sself, *args, **kwargs):
				pass
			def notify(sself, *args, **kwargs):
				pass
		
		self.subject.addObserver(Observer())
		self.observable.changed(self.request)
		
		self.assertTrue(self.stream.getvalue().find("noRecordsMatch") > -1)

	def testSetsInHeader(self):
		self.request.args = {'verb':['ListRecords'], 'metadataPrefix': ['oai_dc']}
		
		class Observer:
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				self.assertEquals('oai_dc', partName)
				self.assertEquals('0', continueAt)
				return ['id_0&0', 'id_1&1']
					
			def write(sself, sink, id, partName):
				if partName == 'oai_dc':
					sink.write('<some:recorddata xmlns:some="http://some.example.org" id="%s"/>' % id.replace('&', '&amp;'))
				elif partName == '__stamp__':
					sink.write("""<__stamp__>
			<datestamp>DATESTAMP_FOR_TEST</datestamp>
		</__stamp__>""")
				elif partName == '__sets__':
					sink.write("""<__sets__><set><setSpec>one:two:three</setSpec><setName>Three Piggies</setName></set><set><setSpec>one:two:four</setSpec><setName>Four Chickies</setName></set></__sets__>""")
				else:
					self.fail(partName + ' is unexpected')
			
			def isAvailable(sself, id, partName):
				if partName == 'oai_dc' or partName == '__sets__':
					return True, True
				return True, False
			
			def undo(sself, *args, **kwargs):
				pass
			def notify(sself, *args, **kwargs):
				pass
		
		self.subject.addObserver(Observer())
		self.observable.changed(self.request)
		
		self.assertTrue("<setSpec>one:two:three</setSpec>" in self.stream.getvalue())
		self.assertTrue("<setSpec>one:two:four</setSpec>" in self.stream.getvalue())	
		
	def testListRecordsUsingMetadataPrefix(self):
		self.request.args = {'verb':['ListRecords'], 'metadataPrefix': ['oai_dc'], 'set': ['SET']}
		
		class Observer:
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				self.assertEquals('SET', oaiSet)
				return []
					
			def undo(sself, *args, **kwargs):
				pass
			def notify(sself, *args, **kwargs):
				pass
		
		self.subject.addObserver(Observer())
		self.observable.changed(self.request)
		
