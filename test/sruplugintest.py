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
    
    def testExplain(self):
        stream = StringIO()
        self.request.write = stream.write
        configuration = {
            'server.host': 'TEST_SERVER_HOST',
            'server.port': 'TEST_SERVER_PORT',
            'server.description': 'TEST_SERVER_DESCRIPTION',
            'server.modifieddate': 'TEST_SERVER_DATE'
        }
        self.request.getenv = configuration.get
        self.assertEquals(SUCCESS, self.plugin.validate())
        self.plugin.process()
        self.assertEqualsWS("""<?xml version="1.0" encoding="UTF-8"?>
<srw:explainResponse xmlns:srw="http://www.loc.gov/zing/srw/"
xmlns:zr="http://explain.z3950.org/dtd/2.0/">
<srw:version>1.1</srw:version>
<srw:record>
    <srw:recordPacking>xml</srw:recordPacking>
    <srw:recordSchema>http://explain.z3950.org/dtd/2.0/</srw:recordSchema>
    <srw:recordData>
        <zr:explain>
            <zr:serverInfo wsdl="http://TEST_SERVER_HOST:TEST_SERVER_PORT/database" protocol="SRU" version="1.1">
                <host>TEST_SERVER_HOST</host>
                <port>TEST_SERVER_PORT</port>
                <database>database</database>
            </zr:serverInfo>
            <zr:databaseInfo>
                <title lang="en" primary="true">SRU Database</title>
                <description lang="en" primary="true">TEST_SERVER_DESCRIPTION</description>
            </zr:databaseInfo>
            <zr:metaInfo>
                <dateModified>TEST_SERVER_DATE</dateModified>
            </zr:metaInfo>
        </zr:explain>
    </srw:recordData>
</srw:record>
</srw:explainResponse>
""", stream.getvalue())
    
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
        
        plugin = SRUPlugin(request)
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
        hits = MockHits(2)
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
</srw:searchRetrieveResponse>
""", resultStream.getvalue())
        
    def testExtraResponseDataHandlerNoHandler(self):
        resultStream = StringIO()
        self.plugin.write = resultStream.write
        self.plugin._writeExtraResponseData(["id_%s" % i for i in range(10)])
        self.assertEquals('' , resultStream.getvalue())
    
    def testExtraResponseDataHandlerNoData(self):
        resultStream = StringIO()
        
        class TestHandler:
            def extraResponseData(self, *args):
                return []
        
        self.plugin.write = resultStream.write
        self.plugin.addObserver(TestHandler())
        self.plugin._writeExtraResponseData(["id_%s" % i for i in range(10)])
        
        self.assertEquals('' , resultStream.getvalue())
        
    def testExtraResponseDataHandlerWithData(self):
        resultStream = StringIO()
        
        class TestHandler:
            def extraResponseData(self, *args):
                return ["<someD", "ata/>"]
        
        self.plugin.write = resultStream.write
        self.plugin.addObserver(TestHandler())
        self.plugin._writeExtraResponseData(["id_%s" % i for i in range(10)])
        
        self.assertEquals('<srw:extraResponseData><someData/></srw:extraResponseData>' , resultStream.getvalue())
        
    def testNextRecordPosition(self):
        request = CallTrace('Request')
        request.args = {'version':['1.1'], 'operation':['searchRetrieve'],
            'query':['field=value'], 'x-recordSchema':['extra'], 'startRecord': ['10'], 'maximumRecords': ['15']}
        request.database = 'database'
        hits = MockHits(100)
        observer = MockListeners(hits)
            
        resultStream = StringIO()
        request.write = resultStream.write

        plugin = SRUPlugin(request)
        plugin.addObserver(observer)
        plugin.process()
        self.assertTrue("<srw:nextRecordPosition>25</srw:nextRecordPosition>" in resultStream.getvalue(), resultStream.getvalue())

        
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
    
    def __init__(self, size):
        self.size = size
    
    def __len__(self):
        return self.size
    
    def __getslice__(self, start, stop):
        self.slice_start = start
        self.slice_stop = stop
        return [str(i) for i in range(start, min(self.size, stop))]
