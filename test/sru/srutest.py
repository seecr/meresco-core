## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school.
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
#remove at the end...
from meresco.legacy.plugins.sruplugin import SRUPlugin, SRUDiagnostic, MANDATORY_PARAMETER_NOT_SUPPLIED, UNSUPPORTED_PARAMETER, UNSUPPORTED_VERSION, UNSUPPORTED_OPERATION, UNSUPPORTED_PARAMETER_VALUE, QUERY_FEATURE_UNSUPPORTED, registerOn

from meresco.components.sru.sru import Sru, SruException

from cq2utils.calltrace import CallTrace
from cStringIO import StringIO
from cq2utils.cq2testcase import CQ2TestCase
from cqlparser.cqlcomposer import compose as cqlCompose
import traceback

SUCCESS = "SUCCESS"

class SruTest(CQ2TestCase):

    def testExplain(self):
        component = Sru(host='TEST_SERVER_HOST', port='TEST_SERVER_PORT', description='TEST_SERVER_DESCRIPTION', modifiedDate='TEST_SERVER_DATE')

        result = "".join(list(component.handleRequest(RequestURI='/DATABASE/sru')))
        self.assertEqualsWS("""<?xml version="1.0" encoding="UTF-8"?>
<srw:explainResponse xmlns:srw="http://www.loc.gov/zing/srw/"
xmlns:zr="http://explain.z3950.org/dtd/2.0/">
<srw:version>1.1</srw:version>
<srw:record>
    <srw:recordPacking>xml</srw:recordPacking>
    <srw:recordSchema>http://explain.z3950.org/dtd/2.0/</srw:recordSchema>
    <srw:recordData>
        <zr:explain>
            <zr:serverInfo wsdl="http://TEST_SERVER_HOST:TEST_SERVER_PORT/DATABASE" protocol="SRU" version="1.1">
                <host>TEST_SERVER_HOST</host>
                <port>TEST_SERVER_PORT</port>
                <database>DATABASE</database>
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
""", result)

    def testParseArguments(self):
        component = Sru(host='', port='', description='', modifiedDate='')
        database, command, arguments = component._parseUri('/db/cmd?arg=something')
        self.assertEquals(('db', 'cmd', {'arg': ['something']}), (database, command, arguments))

    def testMandatoryArgumentsSupplied(self):
        error = MANDATORY_PARAMETER_NOT_SUPPLIED
        self._validate(SUCCESS, {})
        self._validate(error, {'version':['1.1']})
        self._validate(error, {'version':['1.1'], 'query':['']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['x'], 'operation':['searchRetrieve']})

    def testValidateAllowedArguments(self):
        error = UNSUPPORTED_PARAMETER
        self._validate(error, {'version':['1.1'], 'query':['x'], 'operation':['searchRetrieve'], 'niet geldig':['bla']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['x'], 'operation':['searchRetrieve'], 'x-whatever-comes-after-an-x': ['something']})

    def testValidVersion(self):
        error = UNSUPPORTED_VERSION
        self._validate(error, {'version':['1.0'], 'query':['twente'], 'operation':['searchRetrieve']})
        self._validate(error, {'version':['2.0'], 'query':['twente'], 'operation':['searchRetrieve']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve']})

    def testValidOperation(self):
        error = UNSUPPORTED_OPERATION
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['']})
        self._validate(error,{'version':['1.1'], 'query':['twente'], 'operation':['unsupportedOperation']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve']})

    def testValidStartRecord(self):
        error = UNSUPPORTED_PARAMETER_VALUE
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['']})
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['A']})
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['-1']})
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['0']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['1']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'startRecord':['999999999']})

    def testValidMaximumRecords(self):
        error = UNSUPPORTED_PARAMETER_VALUE
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['']})
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['A']})
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['-1']})
        self._validate(error, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['0']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['1']})
        self._validate(SUCCESS, {'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords':['99']})

    def testMaximumMaximumRecords(self):
        component = Sru('', '', '', '', maximumMaximumRecords=100)
        try:
            component._createSruQuery({'version':['1.1'], 'query':['twente'], 'operation':['searchRetrieve'], 'maximumRecords': ['101']})
            self.fail()
        except SruException, e:
            self.assertEquals(UNSUPPORTED_PARAMETER_VALUE, [e.code, e.message])

    def testValidateCQLSyntax(self):
        error = UNSUPPORTED_PARAMETER_VALUE
        self._validate(SUCCESS, {'version':['1.1'], 'query':['TERM'], 'operation':['searchRetrieve'], 'startRecord':['1']})
        self._validate(QUERY_FEATURE_UNSUPPORTED, {'version':['1.1'], 'query':['TERM1)'], 'operation':['searchRetrieve']})

    def _validate(self, error, arguments):
        component = Sru('', '', '', '')
        try:
            operation, arguments = component._parseArguments(arguments)
            if operation == "searchRetrieve":
                component._createSruQuery(arguments)
            if error != SUCCESS:
                self.fail("Expected error %s but got nothing"  % error)
        except SruException, e:
            self.assertEquals(error, [e.code, e.message])

    def testEchoedSearchRetrieveRequest(self):
        arguments = {'version':['1.1'], 'operation':['searchRetrieve'], 'query':['query >= 3']}
        component = Sru('', '', '', '')

        result = "".join(list(component._writeEchoedSearchRetrieveRequest(arguments)))
        self.assertEqualsWS("""<srw:echoedSearchRetrieveRequest>
    <srw:version>1.1</srw:version>
    <srw:query>query &gt;= 3</srw:query>
</srw:echoedSearchRetrieveRequest>""", result)

    def testEchoedSearchRetrieveRequestWithExtraRequestData(self):
        arguments = {'version':['1.1'], 'operation':['searchRetrieve'], 'query':['query >= 3']}
        observer = CallTrace('ExtraRequestData', returnValues={'echoedExtraRequestData': 'some extra request data'})
        component = Sru('', '', '', '')
        component.addObserver(observer)

        result = "".join(list(component._writeEchoedSearchRetrieveRequest(arguments)))
        self.assertEqualsWS("""<srw:echoedSearchRetrieveRequest>
    <srw:version>1.1</srw:version>
    <srw:query>query &gt;= 3</srw:query>
    <srw:extraRequestData>some extra request data</srw:extraRequestData>
</srw:echoedSearchRetrieveRequest>""",result)

    def testExtraResponseDataHandlerNoHandler(self):
        component = Sru('', '', '', '')
        hits = ["id_%s" % i for i in range(10)]
        result = "".join(list(component._writeExtraResponseData({}, hits)))
        self.assertEquals('' , result)

    def testExtraResponseDataHandlerNoData(self):
        class TestHandler:
            def extraResponseData(self, *args):
                return (f for f in [])

        component = Sru('', '', '', '')
        component.addObserver(TestHandler())
        hits = ["id_%s" % i for i in range(10)]
        result = "".join(list(component._writeExtraResponseData({}, hits)))
        self.assertEquals('' , result)

    def testExtraResponseDataHandlerWithData(self):
        class TestHandler:
            def extraResponseData(self, *args):
                return (f for f in ["<someD", "ata/>"])

        component = Sru('', '', '', '')
        component.addObserver(TestHandler())
        hits = ["id_%s" % i for i in range(10)]
        result = "".join(list(component._writeExtraResponseData({}, hits)))
        self.assertEquals('<srw:extraResponseData><someData/></srw:extraResponseData>' , result)

    def testNextRecordPosition(self):
        hits = MockHits(100)
        observer = MockListeners(hits)

        component = Sru('', '', '', '')
        component.addObserver(observer)
        result = "".join(list(component.handleRequest(RequestURI='/database/sru?version=1.1&operation=searchRetrieve&query=field%3Dvalue&x-recordSchema=extra&startRecord=10&maximumRecords=15')))

        self.assertTrue("<srw:nextRecordPosition>25</srw:nextRecordPosition>" in result, result)

    def testSearchRetrieve(self):
        arguments = {'version':['1.1'], 'operation':['searchRetrieve'],  'query':['field=value'], 'x-recordSchema':['extra']}
        'database'
        hits = MockHits(2)
        observer = MockListeners(hits)

        component = Sru('', '', '', '')
        component.addObserver(observer)
        result = "".join(list(component.handleRequest(RequestURI='/database/sru?version=1.1&operation=searchRetrieve&query=field%3Dvalue&x-recordSchema=extra')))

        self.assertTrue(observer.executeCQLCalled)
        self.assertEquals('field=value', cqlCompose(observer.cqlQuery))
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
""", result)

class MockListeners:
    def __init__(self, executeCQLResult):
        self.executeCQLResult = executeCQLResult
        self.writtenRecords = []

    def executeCQL(self, cqlQuery, sortKey, sortDirection):
        self.executeCQLCalled = True
        self.cqlQuery = cqlQuery
        self.sortKey = sortKey
        self.sortDirection = sortDirection
        return self.executeCQLResult

    def writeRecord(self, recordId, recordSchema, recordPacking):
        self.writtenRecords.append((recordId, recordSchema, recordPacking))
        yield "<MOCKED_WRITTEN_DATA>%s-%s</MOCKED_WRITTEN_DATA>" % (recordId, recordSchema)

class MockHits:

    def __init__(self, size):
        self.size = size

    def __len__(self):
        return self.size

    def __getslice__(self, start, stop):
        self.slice_start = start
        self.slice_stop = stop
        return [str(i) for i in range(start, min(self.size, stop))]
