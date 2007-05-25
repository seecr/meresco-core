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

import unittest
from plugins.sruplugin import SUCCESS, SRUPlugin, SRUDiagnostic, MANDATORY_PARAMETER_NOT_SUPPLIED, UNSUPPORTED_PARAMETER, UNSUPPORTED_VERSION, UNSUPPORTED_OPERATION, UNSUPPORTED_PARAMETER_VALUE, QUERY_FEATURE_UNSUPPORTED, registerOn
from cq2utils.calltrace import CallTrace
from cStringIO import StringIO
from cq2utils.cq2testcase import CQ2TestCase
import traceback

class SRUPluginTest(CQ2TestCase):

	def setUp(self):
		CQ2TestCase.setUp(self)
		self.request = CallTrace('Request')
		self.request.args = {}
		self.request.database = 'database'
		self.searchInterface = None
		self.plugin = SRUPlugin(self.request, self.searchInterface)
		
	def testRegistry(self):
		registry = CallTrace('PluginRegistry')
		registerOn(registry)
		self.assertEquals(1, len(registry.calledMethods))
		self.assertEquals("registerByCommand('sru', <class plugins.sruplugin.SRUPlugin>)", str(registry.calledMethods[0]))
		
	def logException(self):
		print traceback.format_exc()

	def testExplain(self):
		stream = StringIO()
		self.request.write = stream.write
		configuration = {
			'server.host': 'somehost',
			'server.port': '3457',
			'server.description': 'description',
			'server.modifieddate': 'yesterday'
		}
		self.request.getenv = configuration.get
		self.assertEquals(SUCCESS, self.plugin.validate())
		self.plugin.process()
		self.assertEqualsWS(EXPLAIN_RESULT, stream.getvalue())
	
	def testGetOperation(self):
		self.plugin._arguments = {'operation':['explain']}
		self.assertEquals("explain", self.plugin.getOperation())
		self.plugin._arguments = {'operation':['searchRetrieve']}
		self.assertEquals("searchRetrieve", self.plugin.getOperation())
				
	
	def testMandatoryArgumentsSupplied(self):
		error = MANDATORY_PARAMETER_NOT_SUPPLIED
		self.validate(error, {'version':['1.1']})
		self.validate(error, {'version':['1.1'], 'query':['']})
		self.validate(SUCCESS, {'version':['1.1'], 'query':['x'], 'operation':['searchRetrieve']})

	def test_validateAllowedArguments(self):
		error = UNSUPPORTED_PARAMETER
		self.validate(error, {'version':['1.1'], 'query':['x'], 'operation':['searchRetrieve'], 'niet geldig':['bla']})
		self.validate(SUCCESS, {'version':['1.1'], 'query':['x'], 'operation':['searchRetrieve'], 'x-whatever-comes-after-an-x': ['something']})
			
	def testValidVersion(self):
		error = UNSUPPORTED_VERSION
		self.validate(error, {'version':['1.0'], 'query':['twente'], 'operation':['searchRetrieve']})
		self.validate(error, {'version':['2.0'], 'query':['twente'], 'operation':['searchRetrieve']})	
		self.validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve']})	
		
	def testValidOperation(self):
		error = UNSUPPORTED_OPERATION
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['']})	
		self.validate(error,{'version':['1.1'], 'query':['twente'], 'operation':['unsupportedOperation']})	
		self.validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve']})	
		
	def testValidStartRecord(self):
		error = UNSUPPORTED_PARAMETER_VALUE
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['']})	
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['A']})	
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['-1']})	
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['0']})	
		self.validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['1']})	
		self.validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['999999999']})	
		
	def testValidMaximumRecords(self):
		error = UNSUPPORTED_PARAMETER_VALUE
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['']})	
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['A']})	
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['-1']})	
		self.validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['0']})	
		self.validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['1']})	
		self.validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['999999999']})	

	def testValidateCQLSyntax(self):
		error = UNSUPPORTED_PARAMETER_VALUE
		self.validate(SUCCESS, {'version':['1.1'], 'query':['TERM'], 'operation':['searchRetrieve'], 'startRecord':['1']})
		self.validate(QUERY_FEATURE_UNSUPPORTED, {'version':['1.1'], 'query':['TERM1)'], 'operation':['searchRetrieve']})

	def validate(self, code, aDict):
		NO_DETAILS = 2
		self.plugin._arguments = aDict
		self.assertEquals(code, self.plugin._validate()[:NO_DETAILS])
				
	def testEchoedSearchRetrieveRequest(self):
		request = CallTrace('Request')
		request.args = {'version':['1.1'], 'operation':['searchRetrieve'],
			'query':['query >= 3']}
			
		b = StringIO()
		request.write = b.write
		mock = CallTrace('ExtraRequestData')
		
		plugin = SRUPlugin(request, self.searchInterface)
		plugin._writeEchoedExtraRequestData = mock._writeEchoedExtraRequestData
		
		plugin._writeEchoedSearchRetrieveRequest()
		self.assertEqualsWS("""<srw:echoedSearchRetrieveRequest>
	<srw:version>1.1</srw:version>
	<srw:query>query &gt;= 3</srw:query>
</srw:echoedSearchRetrieveRequest>""", b.getvalue())
		
		self.assertEquals(1, len(mock.calledMethods))
		self.assertEquals('_writeEchoedExtraRequestData()', str(mock.calledMethods[0]))
				
	def testSearchRetrieve(self):
		request = CallTrace('Request')
		request.args = {'version':['1.1'], 'operation':['searchRetrieve'],
			'query':['field=value'], 'x-recordSchema':['extra']}
		request.database = 'database'
			
		interface = MockSearchInterface()
		interface.search_answer = MockSearchResult()
			
		resultStream = StringIO()
		request.write = resultStream.write

		plugin = SRUPlugin(request, interface)
		
		plugin.process()
		
		self.assertTrue(interface.called, resultStream.getvalue())
		sruQuery = interface.search_argument
		self.assertEquals('field=value', sruQuery.query)
		self.assertEquals(1, sruQuery.startRecord)
		self.assertEquals(10, sruQuery.maximumRecords)
		self.assertEquals(None, sruQuery.sortBy)
		self.assertEquals(None, sruQuery.sortDirection)
		self.assertEquals('database', sruQuery.database)
		self.assertEqualsWS(RESULT, resultStream.getvalue())
		
	def testEmptyRecordWhenInconsistancyExistsBetweenIndexAndStorage(self):
		"""
		JJ: Evil code! If there is an inconsistency between the index and the storage, then it is possible for the storage being asked to retrieve a document that does not exist. This leads to an StorageException which currently floats up to the SRU interface generating an Diagnostics. This messes up the SRU response. Therefor it now writes an empty record to indicate something went wrong. There will need to be a better solution implemented for this, but currently that is not within the scope of this task.
		"""
		
		request = CallTrace('Request')
		request.args = {'version':['1.1'], 'operation':['searchRetrieve'],
			'query':['field=value'], 'x-recordSchema': ['extra']}
		request.database = 'database'
			
		interface = MockSearchInterface()
		interface.search_answer = MockSearchResultWithException()
			
		resultStream = StringIO()
		request.write = resultStream.write

		plugin = SRUPlugin(request, interface)
		
		plugin.process()
		
		self.assertTrue(interface.called, resultStream.getvalue())
		self.assertEqualsWS(RESULT_WITH_EMPTY_RECORD, resultStream.getvalue())
		
class MockSearchInterface:
	def __init__(self):
		self.called = False
	def search(self, sruQuery):
		self.called = True
		self.search_argument = sruQuery
		return self.search_answer
	
class MockSearchResult:
	def getNumberOfRecords(self):
		return 0
	
	def getRecords(self):
		return (MockSearchRecord(i) for i in xrange(2))
	
	def getNextRecordPosition(self):
		return 3
	
	def writeExtraResponseDataOn(self, aStream):
		aStream.write("<numberOfRecords>20</numberOfRecords>")

class MockSearchResultWithException:
	def getNumberOfRecords(self):
		return 0
	
	def getRecords(self):
		for i in xrange(2):
			if i == 1:
				yield MockEmptySearchRecord(i)
			else:
				yield MockSearchRecord(i)
	
	def getNextRecordPosition(self):
		return 3
	
	def writeExtraResponseDataOn(self, aStream):
		aStream.write("<numberOfRecords>20</numberOfRecords>")

class MockEmptySearchRecord:
	def __init__(self, aNumber):
		self.aNumber = aNumber
			
	def writeDataOn(self, recordSchema, aStream):
		pass	

class MockSearchRecord:
	def __init__(self, aNumber):
		self.aNumber = aNumber
		

	def writeDataOn(self, recordSchema, aStream):
		if recordSchema == 'dc':
			aStream.write('<line>')
			aStream.write('<number>%d</number>' % self.aNumber)
			aStream.write('</line>')
		elif recordSchema == 'extra':
			aStream.write('<extraline>')
			aStream.write('<number>%d</number>' % self.aNumber)
			aStream.write('</extraline>')
		

RESULT = """<?xml version="1.0" encoding="UTF-8"?>
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" xmlns:xcql="http://www.loc.gov/zing/cql/xcql/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<srw:version>1.1</srw:version>
<srw:numberOfRecords>0</srw:numberOfRecords>
<srw:records>
	<srw:record>
		<srw:recordSchema>dc</srw:recordSchema>
		<srw:recordPacking>xml</srw:recordPacking>
		<srw:recordData><line><number>0</number></line></srw:recordData>
		<srw:extraRecordData>
			<recordData recordSchema="extra">
				<extraline><number>0</number></extraline>
			</recordData>
		</srw:extraRecordData>
	</srw:record>
	<srw:record>
		<srw:recordSchema>dc</srw:recordSchema>
		<srw:recordPacking>xml</srw:recordPacking>
		<srw:recordData><line><number>1</number></line></srw:recordData>
		<srw:extraRecordData>
			<recordData recordSchema="extra">
				<extraline><number>1</number></extraline>
			</recordData>
		</srw:extraRecordData>
	</srw:record>
</srw:records>
<srw:nextRecordPosition>3</srw:nextRecordPosition>
<srw:echoedSearchRetrieveRequest>
	<srw:version>1.1</srw:version>
	<srw:query>field=value</srw:query>
	<srw:x-recordSchema>extra</srw:x-recordSchema>
</srw:echoedSearchRetrieveRequest>
<srw:extraResponseData>
	<numberOfRecords>20</numberOfRecords>
</srw:extraResponseData>
</srw:searchRetrieveResponse>
"""

EXPLAIN_RESULT = """<?xml version="1.0" encoding="UTF-8"?>
<srw:explainResponse xmlns:srw="http://www.loc.gov/zing/srw/"
xmlns:zr="http://explain.z3950.org/dtd/2.0/">
<srw:version>1.1</srw:version>
<srw:record>
	<srw:recordPacking>XML</srw:recordPacking>
	<srw:recordSchema>http://explain.z3950.org/dtd/2.0/</srw:recordSchema>
	<srw:recordData>
		<zr:explain>
			<zr:serverInfo wsdl="http://somehost:3457/database" protocol="SRU" version="1.1">
				<host>somehost</host>
				<port>3457</port>
				<database>database</database>
			</zr:serverInfo>
			<zr:databaseInfo>
				<title lang="en" primary="true">SRU Database</title>
				<description lang="en" primary="true">description</description>
			</zr:databaseInfo>
			<zr:metaInfo>
				<dateModified>yesterday</dateModified>
			</zr:metaInfo>
		</zr:explain>
	</srw:recordData>
</srw:record>
</srw:explainResponse>
"""

RESULT_WITH_EMPTY_RECORD = """<?xml version="1.0" encoding="UTF-8"?>
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" xmlns:xcql="http://www.loc.gov/zing/cql/xcql/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<srw:version>1.1</srw:version>
<srw:numberOfRecords>0</srw:numberOfRecords>
<srw:records>
	<srw:record>
		<srw:recordSchema>dc</srw:recordSchema>
		<srw:recordPacking>xml</srw:recordPacking>
		<srw:recordData><line><number>0</number></line></srw:recordData>
		<srw:extraRecordData>
			<recordData recordSchema="extra">
				<extraline><number>0</number></extraline>
			</recordData>
		</srw:extraRecordData>
	</srw:record>
	<srw:record>
		<srw:recordSchema>dc</srw:recordSchema>
		<srw:recordPacking>xml</srw:recordPacking>
		<srw:recordData></srw:recordData>
		<srw:extraRecordData>
			<recordData recordSchema="extra"></recordData>
		</srw:extraRecordData>
	</srw:record>
</srw:records>
<srw:nextRecordPosition>3</srw:nextRecordPosition>
<srw:echoedSearchRetrieveRequest>
	<srw:version>1.1</srw:version>
	<srw:query>field=value</srw:query>
	<srw:x-recordSchema>extra</srw:x-recordSchema>
</srw:echoedSearchRetrieveRequest>
<srw:extraResponseData>
	<numberOfRecords>20</numberOfRecords>
</srw:extraResponseData>
</srw:searchRetrieveResponse>
"""
