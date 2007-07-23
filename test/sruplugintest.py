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

import unittest
from meresco.legacy.plugins.sruplugin import SUCCESS, SRUPlugin, SRUDiagnostic, MANDATORY_PARAMETER_NOT_SUPPLIED, UNSUPPORTED_PARAMETER, UNSUPPORTED_VERSION, UNSUPPORTED_OPERATION, UNSUPPORTED_PARAMETER_VALUE, QUERY_FEATURE_UNSUPPORTED, registerOn
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
        self.plugin = SRUPlugin(self.request)
        
    def testRegistry(self):
        registry = CallTrace('PluginRegistry')
        registerOn(registry)
        self.assertEquals(1, len(registry.calledMethods))
        self.assertEquals("registerByCommand('sru', <class 'meresco.legacy.plugins.sruplugin.SRUPlugin'>)", str(registry.calledMethods[0]))
        
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
        self.assertEquals(code, self.plugin.validate()[:NO_DETAILS])
                
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
        hits = MockHits()
        observer = MockListeners(hits)
            
        resultStream = StringIO()
        request.write = resultStream.write

        plugin = SRUPlugin(request)
        plugin.addObserver(observer)
        plugin.process()
        
        self.assertTrue(observer.executeCQLCalled)
        self.assertEquals('field=value', observer.cqlQuery)
        self.assertEquals(0, hits.slice_start)
        self.assertEquals(10, hits.slice_stop)
        
        self.assertEquals(4, len(observer.writtenRecords))
        self.assertEquals(('0', 'dc', 'xml'), observer.writtenRecords[0])
        self.assertEquals(('0', 'extra', 'xml'), observer.writtenRecords[1])
        
        self.assertEqualsWS("""<?xml version="1.0" encoding="UTF-8"?>
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" xmlns:xcql="http://www.loc.gov/zing/cql/xcql/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<srw:version>1.1</srw:version>
<srw:numberOfRecords>2</srw:numberOfRecords>
<srw:records>
    <srw:record>
        <srw:recordSchema>dc</srw:recordSchema>
        <srw:recordPacking>xml</srw:recordPacking>
        <srw:recordData>
            <MOCKED_WRITTEN_DATA>0-dc</MOCKED_WRITTEN_DATA>
        </srw:recordData>
        <srw:extraRecordData><recordData recordSchema="extra">
            <MOCKED_WRITTEN_DATA>0-extra</MOCKED_WRITTEN_DATA>
        </recordData></srw:extraRecordData>
    </srw:record>
    <srw:record>
        <srw:recordSchema>dc</srw:recordSchema>
        <srw:recordPacking>xml</srw:recordPacking>
        <srw:recordData>
            <MOCKED_WRITTEN_DATA>1-dc</MOCKED_WRITTEN_DATA>
        </srw:recordData>
        <srw:extraRecordData><recordData recordSchema="extra">
            <MOCKED_WRITTEN_DATA>1-extra</MOCKED_WRITTEN_DATA>
        </recordData></srw:extraRecordData>
    </srw:record>
</srw:records>
<srw:echoedSearchRetrieveRequest>
    <srw:version>1.1</srw:version>
    <srw:query>field=value</srw:query>
    <srw:x-recordSchema>extra</srw:x-recordSchema>
</srw:echoedSearchRetrieveRequest>
<srw:extraResponseData>
</srw:extraResponseData>
</srw:searchRetrieveResponse>
""", resultStream.getvalue())
        
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
        
    def testExtraResponseDataHandler(self):
        notifications = []
        class TestHandler:
            def writeExtraResponseData(self, *args):
                notifications.append(args)
        
        self.plugin.addObserver(TestHandler())
        self.plugin._writeExtraResponseData(MockSearchResult())
        self.assertEquals([(self.plugin, )], notifications)
        
    def testNextRecordPosition(self):
        self.fail("Klaas")
        
    def testIsEmptyExtraResponseDataAllowed(self):
        self.fail("Johan")
        
class MockListeners:
    def __init__(self, executeCQLResult):
        self.executeCQLResult = executeCQLResult
        self.writtenRecords = []
        
    def executeCQL(self, cqlQuery):
        self.executeCQLCalled = True
        self.cqlQuery = cqlQuery
        return self.executeCQLResult
    
    def writeRecord(self, sink, recordId, recordSchema, recordPacking):
        self.writtenRecords.append((recordId, recordSchema, recordPacking))
        sink.write("<MOCKED_WRITTEN_DATA>%s-%s</MOCKED_WRITTEN_DATA>" % (recordId, recordSchema))
    
class MockHits:
    
    #def getRecords(self):
        #return (MockSearchRecord(i) for i in xrange(2))
    def __len__(self):
        return 2
    
    def __getslice__(self, start, stop):
        self.slice_start = start
        self.slice_stop = stop
        for i in range(2):
            yield str(i)
            

    
    #20, 3

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
