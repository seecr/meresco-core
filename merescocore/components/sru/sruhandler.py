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
from cgi import parse_qs
from urlparse import urlsplit
from urllib import unquote
from xml.sax.saxutils import escape as xmlEscape

from merescocore.framework import Observable, decorate
from merescocore.components.sru.sruquery import SRUQuery, SRUQueryParameterException, SRUQueryParseException
from merescocore.components.http import utils as httputils

from cqlparser import parseString as parseCQL
from weightless import compose

VERSION = '1.1'

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

OFFICIAL_REQUEST_PARAMETERS = {
    'explain': ['operation', 'version', 'stylesheet', 'extraRequestData', 'recordPacking'],
    'searchRetrieve': ['version','query','startRecord','maximumRecords','recordPacking','recordSchema',
'recordXPath','resultSetTTL','sortKeys','stylesheet','extraRequestData','operation']}

MANDATORY_PARAMETERS = {
    'explain':['version', 'operation'],
    'searchRetrieve':['version', 'operation', 'query']}

SUPPORTED_OPERATIONS = ['explain', 'searchRetrieve']

RESPONSE_HEADER = """<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" xmlns:xcql="http://www.loc.gov/zing/cql/xcql/" xmlns:dc="http://purl.org/dc/elements/1.1/">
"""

RESPONSE_FOOTER = """</srw:searchRetrieveResponse>"""

DIAGNOSTIC = """<diagnostic xmlns="http://www.loc.gov/zing/srw/diagnostics/">
        <uri>info://srw/diagnostics/1/%s</uri>
        <details>%s</details>
        <message>%s</message>
    </diagnostic>"""

DIAGNOSTICS = """<diagnostics>
%s
</diagnostics>
""" % DIAGNOSTIC

ECHOED_PARAMETER_NAMES = ['version', 'query', 'startRecord', 'maximumRecords', 'recordPacking', 'recordSchema', 'recordXPath', 'resultSetTTL', 'sortKeys', 'stylesheet', 'x-recordSchema']

GENERAL_SYSTEM_ERROR = [1, "General System Error"]
SYSTEM_TEMPORARILY_UNAVAILABLE = [2, "System Temporarily Unavailable"]
UNSUPPORTED_OPERATION = [4, "Unsupported Operation"]
UNSUPPORTED_VERSION = [5, "Unsupported Version"]
UNSUPPORTED_PARAMETER_VALUE = [6, "Unsupported Parameter Value"]
MANDATORY_PARAMETER_NOT_SUPPLIED = [7, "Mandatory Parameter Not Supplied"]
UNSUPPORTED_PARAMETER = [8, "Unsupported Parameter"]
QUERY_FEATURE_UNSUPPORTED = [48, "Query Feature Unsupported"]

class SruException(Exception):

    def __init__(self, (code, message), details="No details available"):
        Exception.__init__(self)
        self.code = code
        self.message = message
        self.details = details

class SruHandler(Observable):

    def __init__(self):
        Observable.__init__(self)

    def _writeEchoedSearchRetrieveRequest(self, arguments):
        yield '<srw:echoedSearchRetrieveRequest>'
        for parameterName in ECHOED_PARAMETER_NAMES:
            for value in map(xmlEscape, arguments.get(parameterName, [])):
                yield '<srw:%(parameterName)s>%(value)s</srw:%(parameterName)s>' % locals()

        for chunk in decorate('<srw:extraRequestData>', compose(self.all.echoedExtraRequestData(arguments)), '</srw:extraRequestData>'):
            yield chunk
        yield '</srw:echoedSearchRetrieveRequest>'

    def _writeExtraResponseData(self, arguments, cqlAbstractSyntaxTree):
        return decorate('<srw:extraResponseData>',
            self._extraResponseDataTryExcept(arguments, cqlAbstractSyntaxTree),
            '</srw:extraResponseData>')

    def _extraResponseDataTryExcept(self, arguments, cqlAbstractSyntaxTree):
        try:
            stuffs = compose(self.all.extraResponseData(arguments, cqlAbstractSyntaxTree))
            for stuff in stuffs:
                yield stuff
        except Exception, e:
            yield DIAGNOSTIC % tuple(GENERAL_SYSTEM_ERROR + [xmlEscape(str(e))])

    def _executeCQL(self, cqlAbstractSyntaxTree, start, stop, sortBy, sortDescending, arguments):
        """Hook method (arguments is not used here, may be used in subclasses)"""
        return self.any.executeCQL(
            cqlAbstractSyntaxTree=cqlAbstractSyntaxTree,
            start=start,
            stop=stop,
            sortBy=sortBy,
            sortDescending=sortDescending)

    def searchRetrieve(self, sruQuery, arguments):
        SRU_IS_ONE_BASED = 1

        start = sruQuery.startRecord - SRU_IS_ONE_BASED
        cqlAbstractSyntaxTree = parseCQL(sruQuery.query)
        try:
            total, recordIds = self._executeCQL(
                cqlAbstractSyntaxTree=cqlAbstractSyntaxTree,
                start=start,
                stop=start + sruQuery.maximumRecords,
                sortBy=sruQuery.sortBy,
                sortDescending=sruQuery.sortDescending,
                arguments=arguments)
        except Exception, e:
            yield DIAGNOSTICS % ( QUERY_FEATURE_UNSUPPORTED[0], QUERY_FEATURE_UNSUPPORTED[1], xmlEscape(str(e)))
            return
        yield self._startResults(total)

        recordsWritten = 0
        for recordId in recordIds:
            if not recordsWritten:
                yield '<srw:records>'
            yield self._writeResult(sruQuery, recordId)
            recordsWritten += 1

        if recordsWritten:
            yield '</srw:records>'
            nextRecordPosition = start + recordsWritten
            if nextRecordPosition < total:
                yield '<srw:nextRecordPosition>%i</srw:nextRecordPosition>' % (nextRecordPosition + SRU_IS_ONE_BASED)

        yield self._writeEchoedSearchRetrieveRequest(arguments)
        yield self._writeExtraResponseData(arguments=arguments, cqlAbstractSyntaxTree=cqlAbstractSyntaxTree)
        yield self._endResults()

    def _startResults(self, numberOfRecords):
        yield RESPONSE_HEADER
        yield '<srw:version>%s</srw:version>' % VERSION
        yield '<srw:numberOfRecords>%s</srw:numberOfRecords>' % numberOfRecords

    def _endResults(self):
        yield RESPONSE_FOOTER

    def _writeResult(self, sruQuery, recordId):
        yield '<srw:record>'
        yield '<srw:recordSchema>%s</srw:recordSchema>' % sruQuery.recordSchema
        yield '<srw:recordPacking>%s</srw:recordPacking>' % sruQuery.recordPacking
        yield self._writeRecordData(sruQuery, recordId)
        yield self._writeExtraRecordData(sruQuery, recordId)
        yield '</srw:record>'

    def _writeRecordData(self, sruQuery, recordId):
        yield '<srw:recordData>'

        yield self._catchErrors(self._yieldRecordForRecordPacking(recordId, sruQuery.recordSchema, sruQuery.recordPacking))
        yield '</srw:recordData>'

    def _catchErrors(self, dataGenerator):
        try:
            for stuff in compose(dataGenerator):
                yield stuff
        except Exception, e:
            yield DIAGNOSTIC % tuple(GENERAL_SYSTEM_ERROR + [xmlEscape(str(e))])


    def _writeExtraRecordData(self, sruQuery, recordId):
        if not sruQuery.x_recordSchema:
            raise StopIteration()

        yield '<srw:extraRecordData>'
        for schema in sruQuery.x_recordSchema:
            yield '<recordData recordSchema="%s">' % xmlEscape(schema)
            yield self._catchErrors(self._yieldRecordForRecordPacking(recordId, schema, sruQuery.recordPacking))
            yield '</recordData>'
        yield '</srw:extraRecordData>'

    def _yieldRecordForRecordPacking(self, recordId, recordSchema, recordPacking):
        generator = compose(self.all.yieldRecord(recordId, recordSchema))
        if recordPacking == 'xml':
            for data in generator:
                yield data
        elif recordPacking == 'string':
            for data in generator:
                yield xmlEscape(data)
        else:
            raise Exception("Unknown Record Packing: %s" % recordPacking)

    def explain(self, **kwargs):
        version = VERSION
        host = self._host
        port = self._port
        description = self._description
        modifiedDate = self._modifiedDate
        database = self._database
        return """<srw:explainResponse xmlns:srw="http://www.loc.gov/zing/srw/"
   xmlns:zr="http://explain.z3950.org/dtd/2.0/">
    <srw:version>%(version)s</srw:version>
    <srw:record>
        <srw:recordPacking>xml</srw:recordPacking>
        <srw:recordSchema>http://explain.z3950.org/dtd/2.0/</srw:recordSchema>
        <srw:recordData>
            <zr:explain>
                <zr:serverInfo wsdl="http://%(host)s:%(port)s/%(database)s" protocol="SRU" version="%(version)s">
                    <host>%(host)s</host>
                    <port>%(port)s</port>
                    <database>%(database)s</database>
                </zr:serverInfo>
                <zr:databaseInfo>
                    <title lang="en" primary="true">SRU Database</title>
                    <description lang="en" primary="true">%(description)s</description>
                </zr:databaseInfo>
                <zr:metaInfo>
                    <dateModified>%(modifiedDate)s</dateModified>
                </zr:metaInfo>
            </zr:explain>
        </srw:recordData>
    </srw:record>
</srw:explainResponse>""" % locals()