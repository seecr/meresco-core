## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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
from merescocore.components.sru.sruparser import MANDATORY_PARAMETER_NOT_SUPPLIED, UNSUPPORTED_PARAMETER, UNSUPPORTED_VERSION, UNSUPPORTED_OPERATION, UNSUPPORTED_PARAMETER_VALUE, QUERY_FEATURE_UNSUPPORTED, SruException

from merescocore.components.sru import SruHandler

from cq2utils.calltrace import CallTrace
from cStringIO import StringIO
from cq2utils.cq2testcase import CQ2TestCase
from cqlparser.cqlcomposer import compose as cqlCompose
import traceback

from weightless import compose

SUCCESS = "SUCCESS"

class SruHandlerTest(CQ2TestCase):

    def testEchoedSearchRetrieveRequest(self):
        arguments = {'version':['1.1'], 'operation':['searchRetrieve'], 'query':['query >= 3']}
        component = SruHandler('', '', '', '')

        result = "".join(list(component._writeEchoedSearchRetrieveRequest(arguments)))
        self.assertEqualsWS("""<srw:echoedSearchRetrieveRequest>
    <srw:version>1.1</srw:version>
    <srw:query>query &gt;= 3</srw:query>
</srw:echoedSearchRetrieveRequest>""", result)

    def testEchoedSearchRetrieveRequestWithExtraRequestData(self):
        arguments = {'version':['1.1'], 'operation':['searchRetrieve'], 'query':['query >= 3']}
        observer = CallTrace('ExtraRequestData', returnValues={'echoedExtraRequestData': 'some extra request data'})
        component = SruHandler('', '', '', '')
        component.addObserver(observer)

        result = "".join(list(component._writeEchoedSearchRetrieveRequest(arguments)))
        self.assertEqualsWS("""<srw:echoedSearchRetrieveRequest>
    <srw:version>1.1</srw:version>
    <srw:query>query &gt;= 3</srw:query>
    <srw:extraRequestData>some extra request data</srw:extraRequestData>
</srw:echoedSearchRetrieveRequest>""",result)

    def testExtraResponseDataHandlerNoHandler(self):
        component = SruHandler('', '', '', '')
        hits = ["id_%s" % i for i in range(10)]
        result = "".join(list(component._writeExtraResponseData({}, hits)))
        self.assertEquals('' , result)

    def testExtraResponseDataHandlerNoData(self):
        class TestHandler:
            def extraResponseData(self, *args):
                return (f for f in [])

        component = SruHandler('', '', '', '')
        component.addObserver(TestHandler())
        hits = ["id_%s" % i for i in range(10)]
        result = "".join(list(component._writeExtraResponseData({}, hits)))
        self.assertEquals('' , result)

    def testExtraResponseDataHandlerWithData(self):
        class TestHandler:
            def extraResponseData(self, *args):
                return (f for f in ["<someD", "ata/>"])

        component = SruHandler('', '', '', '')
        component.addObserver(TestHandler())
        hits = ["id_%s" % i for i in range(10)]
        result = "".join(list(component._writeExtraResponseData({}, hits)))
        self.assertEquals('<srw:extraResponseData><someData/></srw:extraResponseData>' , result)

    def testNextRecordPosition(self):
        hits = range(100)
        observer = CallTrace()
        observer.returnValues['executeCQL'] = (10, range(11, 25))

        component = SruHandler('', '', '', '')
        component.addObserver(observer)
        result = "".join(list(component.searchRetrieve(sruQuery=None, startRecord=['11'], maximumRecords = ['15'])))
        self.assertTrue("<srw:nextRecordPosition>26</srw:nextRecordPosition>" in result, result)

        self.assertEquals(10, observer.start) # SRU is 1 based
        self.assertEquals(25, observer.stop)

    def testSearchRetrieve(self):
        arguments = {'version':['1.1'], 'operation':['searchRetrieve'],  'query':['field=value'], 'x-recordSchema':['extra']}
        'database'
        observer = MockListeners(['0','1'])
        component = SruHandler('', '', '', '')
        component.addObserver(observer)
        result = "".join(list(component.handleRequest(RequestURI='/database/sru?version=1.1&operation=searchRetrieve&query=field%3Dvalue&x-recordSchema=extra')))

        self.assertTrue(observer.executeCQLCalled)
        self.assertEquals('field=value', cqlCompose(observer.cqlQuery))
        self.assertEquals(0, observer.start)
        self.assertEquals(10, observer.stop)

        self.assertEquals(4, len(observer.writtenRecords))
        self.assertEquals(('0', 'dc'), observer.writtenRecords[0])
        self.assertEquals(('0', 'extra'), observer.writtenRecords[1])

        self.assertEqualsWS("""HTTP/1.0 200 OK
Content-Type: text/xml; charset=utf-8

<?xml version="1.0" encoding="UTF-8"?>
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

    def testExceptionInWriteRecordData(self):
        class RaisesException(object):
            def yieldRecordForRecordPacking(self, *args):
                raise Exception("Test Exception")
        component = SruHandler('', '', '', '')
        component.addObserver(RaisesException())
        result = "".join(list(compose(component._writeRecordData(CallTrace("Query"), "ID"))))
        self.assertTrue("diagnostic" in result)

    def testExceptionInWriteExtraRecordData(self):
        class RaisesException(object):
            def extraResponseData(self, *args):
                raise Exception("Test Exception")
        component = SruHandler('', '', '', '')
        component.addObserver(RaisesException())
        result = "".join(list(compose(component._writeExtraResponseData("arguments", "hits"))))
        self.assertTrue("diagnostic" in result)

class MockListeners:
    def __init__(self, executeCQLResult):
        self.executeCQLResult = executeCQLResult
        self.writtenRecords = []

    def executeCQL(self, cqlAbstractSyntaxTree, start=0, stop=10, sortBy=None, sortDescending=None):
        self.executeCQLCalled = True
        self.cqlQuery = cqlAbstractSyntaxTree
        self.sortKey = sortBy
        self.sortDirection = sortDescending
        self.start = start
        self.stop = stop
        return len(self.executeCQLResult), self.executeCQLResult[start:stop]

    def yieldRecord(self, recordId, recordSchema):
        self.writtenRecords.append((recordId, recordSchema))
        yield "<MOCKED_WRITTEN_DATA>%s-%s</MOCKED_WRITTEN_DATA>" % (recordId, recordSchema)

