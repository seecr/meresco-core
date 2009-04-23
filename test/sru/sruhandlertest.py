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

from merescocore.components.sru.sruparser import MANDATORY_PARAMETER_NOT_SUPPLIED, UNSUPPORTED_PARAMETER, UNSUPPORTED_VERSION, UNSUPPORTED_OPERATION, UNSUPPORTED_PARAMETER_VALUE, QUERY_FEATURE_UNSUPPORTED, SruException

from merescocore.components.sru import SruHandler, SruParser
from merescocore.components.xml_generic.validate import assertValid
from merescocore.components.xml_generic import schemasPath

from os.path import join


from cq2utils.calltrace import CallTrace
from cStringIO import StringIO
from cq2utils.cq2testcase import CQ2TestCase
from cqlparser.cqlcomposer import compose as cqlCompose
import traceback

from weightless import compose

SUCCESS = "SUCCESS"

class SruHandlerTest(CQ2TestCase):

    def testEchoedSearchRetrieveRequest(self):
        arguments = {'version':'1.1', 'operation':'searchRetrieve', 'query':'query >= 3', 'recordSchema':'schema', 'recordPacking':'string'}
        component = SruHandler()

        result = "".join(list(component._writeEchoedSearchRetrieveRequest(**arguments)))
        self.assertEqualsWS("""<srw:echoedSearchRetrieveRequest>
    <srw:version>1.1</srw:version>
    <srw:query>query &gt;= 3</srw:query>
    <srw:recordPacking>string</srw:recordPacking>
    <srw:recordSchema>schema</srw:recordSchema>
</srw:echoedSearchRetrieveRequest>""", result)

    def testEchoedSearchRetrieveRequestWithExtraRequestData(self):
        arguments = {'version':'1.1', 'operation':'searchRetrieve', 'query':'query >= 3', 'recordSchema':'schema', 'recordPacking':'string'}
        observer = CallTrace('ExtraRequestData', returnValues={'echoedExtraRequestData': 'some extra request data'})
        component = SruHandler()
        component.addObserver(observer)

        result = "".join(list(component._writeEchoedSearchRetrieveRequest(**arguments)))
        self.assertEqualsWS("""<srw:echoedSearchRetrieveRequest>
    <srw:version>1.1</srw:version>
    <srw:query>query &gt;= 3</srw:query>
    <srw:recordPacking>string</srw:recordPacking>
    <srw:recordSchema>schema</srw:recordSchema>
    <srw:extraRequestData>some extra request data</srw:extraRequestData>
</srw:echoedSearchRetrieveRequest>""", result)

    def testExtraResponseDataHandlerNoHandler(self):
        component = SruHandler()
        result = "".join(list(component._writeExtraResponseData(cqlAbstractSyntaxTree=None)))
        self.assertEquals('' , result)

    def testExtraResponseDataHandlerNoData(self):
        class TestHandler:
            def extraResponseData(self, *args, **kwargs):
                return (f for f in [])

        component = SruHandler()
        component.addObserver(TestHandler())
        result = "".join(list(component._writeExtraResponseData(cqlAbstractSyntaxTree=None)))
        self.assertEquals('' , result)

    def testExtraResponseDataHandlerWithData(self):
        argsUsed = []
        kwargsUsed = []
        class TestHandler:
            def extraResponseData(self, *args, **kwargs):
                argsUsed.append(args)
                kwargsUsed.append(kwargs)
                return (f for f in ["<someD", "ata/>"])

        component = SruHandler()
        component.addObserver(TestHandler())
        result = "".join(list(component._writeExtraResponseData(cqlAbstractSyntaxTree=None)))
        self.assertEquals('<srw:extraResponseData><someData/></srw:extraResponseData>' , result)
        self.assertEquals([()], argsUsed)
        self.assertEquals([{'cqlAbstractSyntaxTree': None}], kwargsUsed)
        

    def testNextRecordPosition(self):
        observer = CallTrace()
        observer.returnValues['executeCQL'] = (100, range(11, 26))
        observer.returnValues['yieldRecord'] = "record"
        observer.returnValues['extraResponseData'] = 'extraResponseData'
        observer.returnValues['echoedExtraRequestData'] = 'echoedExtraRequestData'

        component = SruHandler()
        component.addObserver(observer)

        result = "".join(compose(component.searchRetrieve(startRecord=11, maximumRecords=15, query='query', recordPacking='string', recordSchema='schema')))
        self.assertTrue("<srw:nextRecordPosition>26</srw:nextRecordPosition>" in result, result)

        executeCqlCallKwargs = observer.calledMethods[0].kwargs
        self.assertEquals(10, executeCqlCallKwargs['start']) # SRU is 1 based
        self.assertEquals(25, executeCqlCallKwargs['stop'])

    def testSearchRetrieve(self):
        arguments = {'version':'1.1', 'operation':'searchRetrieve',  'recordSchema':'schema', 'recordPacking':'xml', 'query':'field=value', 'startRecord':1, 'maximumRecords':2, 'x_recordSchema':['extra', 'evenmore']}

        observer = CallTrace()
        observer.returnValues['executeCQL'] = (100, range(11, 13))

        yieldRecordCalls = []
        def yieldRecord(recordId, recordSchema):
            yieldRecordCalls.append(1)
            yield "<MOCKED_WRITTEN_DATA>%s-%s</MOCKED_WRITTEN_DATA>" % (recordId, recordSchema)
        observer.yieldRecord = yieldRecord

        observer.returnValues['extraResponseData'] = 'extraResponseData'
        observer.returnValues['echoedExtraRequestData'] = 'echoedExtraRequestData'

        component = SruHandler()
        component.addObserver(observer)

        result = "".join(compose(component.searchRetrieve(**arguments)))
        self.assertEquals(['executeCQL', 'echoedExtraRequestData', 'extraResponseData'], [m.name for m in observer.calledMethods])
        executeCQLMethod, echoedExtraRequestDataMethod, extraResponseDataMethod = observer.calledMethods
        self.assertEquals('executeCQL', executeCQLMethod.name)
        methodKwargs = executeCQLMethod.kwargs
        self.assertEquals('field=value', cqlCompose(methodKwargs['cqlAbstractSyntaxTree']))
        self.assertEquals(0, methodKwargs['start'])
        self.assertEquals(2, methodKwargs['stop'])

        self.assertEquals(6, sum(yieldRecordCalls))

        self.assertEqualsWS("""
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" xmlns:xcql="http://www.loc.gov/zing/cql/xcql/" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <srw:version>1.1</srw:version>
    <srw:numberOfRecords>100</srw:numberOfRecords>
    <srw:records>
        <srw:record>
            <srw:recordSchema>schema</srw:recordSchema>
            <srw:recordPacking>xml</srw:recordPacking>
            <srw:recordData>
                <MOCKED_WRITTEN_DATA>11-schema</MOCKED_WRITTEN_DATA>
            </srw:recordData>
            <srw:extraRecordData>
                <recordData recordSchema="extra">
                    <MOCKED_WRITTEN_DATA>11-extra</MOCKED_WRITTEN_DATA>
                </recordData>
                <recordData recordSchema="evenmore">
                    <MOCKED_WRITTEN_DATA>11-evenmore</MOCKED_WRITTEN_DATA>
                </recordData>
            </srw:extraRecordData>
        </srw:record>
        <srw:record>
            <srw:recordSchema>schema</srw:recordSchema>
            <srw:recordPacking>xml</srw:recordPacking>
            <srw:recordData>
                <MOCKED_WRITTEN_DATA>12-schema</MOCKED_WRITTEN_DATA>
            </srw:recordData>
            <srw:extraRecordData>
                <recordData recordSchema="extra">
                    <MOCKED_WRITTEN_DATA>12-extra</MOCKED_WRITTEN_DATA>
                </recordData>
                <recordData recordSchema="evenmore">
                    <MOCKED_WRITTEN_DATA>12-evenmore</MOCKED_WRITTEN_DATA>
                </recordData>
            </srw:extraRecordData>
        </srw:record>
    </srw:records>
    <srw:nextRecordPosition>3</srw:nextRecordPosition>
    <srw:echoedSearchRetrieveRequest>
        <srw:version>1.1</srw:version>
        <srw:query>field=value</srw:query>
        <srw:startRecord>1</srw:startRecord>
        <srw:maximumRecords>2</srw:maximumRecords>
        <srw:recordPacking>xml</srw:recordPacking>
        <srw:recordSchema>schema</srw:recordSchema>
        <srw:x-recordSchema>extra</srw:x-recordSchema>
        <srw:x-recordSchema>evenmore</srw:x-recordSchema>
        <srw:extraRequestData>echoedExtraRequestData</srw:extraRequestData>
    </srw:echoedSearchRetrieveRequest>
    <srw:extraResponseData>extraResponseData</srw:extraResponseData>
</srw:searchRetrieveResponse>
""", result)
        
        self.assertEquals((), echoedExtraRequestDataMethod.args)
        self.assertEquals(['version', 'recordSchema', 'x_recordSchema', 'sortDescending', 'sortBy', 'maximumRecords', 'startRecord', 'query', 'operation', 'recordPacking'], echoedExtraRequestDataMethod.kwargs.keys())
        self.assertEquals((), extraResponseDataMethod.args)
        self.assertEquals(set(['version', 'recordSchema', 'x_recordSchema', 'sortDescending', 'sortBy', 'maximumRecords', 'startRecord', 'query', 'operation', 'recordPacking', 'cqlAbstractSyntaxTree']), set(extraResponseDataMethod.kwargs.keys()))

    def testExceptionInWriteRecordData(self):
        observer = CallTrace()
        observer.exceptions["yieldRecord"] = Exception("Test Exception")
        component = SruHandler()
        component.addObserver(observer)
        result = "".join(list(compose(component._writeRecordData(recordPacking="string", recordSchema="schema", recordId="ID"))))
        self.assertTrue("diagnostic" in result, result)
        self.assertTrue("Test Exception" in result, result)

    def testExceptionInWriteExtraRecordData(self):
        class RaisesException(object):
            def extraResponseData(self, *args, **kwargs):
                raise Exception("Test Exception")
        component = SruHandler()
        component.addObserver(RaisesException())
        result = "".join(compose(component._writeExtraResponseData(cqlAbstractSyntaxTree=None)))
        self.assertTrue("diagnostic" in result)

    def testDiagnosticOnExecuteCql(self):
        class RaisesException(object):
            def executeCQL(self, *args, **kwargs):
                raise Exception("Test Exception")
        component = SruHandler()
        component.addObserver(RaisesException())
        result = "".join(compose(component.searchRetrieve(startRecord=11, maximumRecords=15, query='query', recordPacking='string', recordSchema='schema')))
        self.assertTrue("diagnostic" in result)

    
    def testValidXml(self):
        component = SruParser()
        sruHandler = SruHandler()
        component.addObserver(sruHandler)
        observer = CallTrace('observer')
        sruHandler.addObserver(observer)
        observer.returnValues['executeCQL'] = (2, ['id0', 'id1'])
        observer.returnValues['echoedExtraRequestData'] = (f for f in [])
        observer.returnValues['extraResponseData'] = (f for f in [])
        observer.returnValues['yieldRecord'] = lambda *args, **kwargs: '<bike/>'

        result = ''.join(compose(component.handleRequest(arguments={'version':['1.1'], 'query': ['aQuery'], 'operation':['searchRetrieve']})))
        header, body = result.split('\r\n'*2)
        assertValid(body, join(schemasPath, 'srw-types.xsd'))
        self.assertTrue('<bike/>' in body)
        
        result = ''.join(compose(component.handleRequest(arguments={'version':['1.1'], 'operation':['searchRetrieve']})))
        header, body = result.split('\r\n'*2)
        assertValid(body, join(schemasPath, 'srw-types.xsd'))
        self.assertTrue('diagnostic' in body)
