## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
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

from meresco.framework import Observable, decorate, compose
from meresco.components.sru.sruquery import SRUQuery, SRUQueryParameterException, SRUQueryParseException
from meresco.components.http import utils as httputils

from cqlparser.cqlparser import parseString as parseCQL

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

class Sru(Observable):

    def __init__(self, host, port, description='Meresco SRU', modifiedDate='1970-01-01T00:00:00Z', defaultRecordSchema="dc", defaultRecordPacking="xml", maximumMaximumRecords=None):
        Observable.__init__(self)
        self._host = host
        self._port = port
        self._description = description
        self._modifiedDate = modifiedDate
        self._defaultRecordSchema = defaultRecordSchema
        self._defaultRecordPacking = defaultRecordPacking
        self._maximumMaximumRecords = maximumMaximumRecords

    def handleRequest(self, port=None, Client=None, RequestURI=None, Method=None, Headers=None, **kwargs):
        database, command, queryArguments = self._parseUri(RequestURI)
        yield httputils.okXml

        yield XML_HEADER
        try:
            operation, arguments = self._parseArguments(queryArguments)
            if operation == "searchRetrieve":
                query = self._createSruQuery(arguments)
        except SruException, e:
            yield DIAGNOSTICS % (e.code, xmlEscape(e.details), xmlEscape(e.message))
            raise StopIteration()

        try:
            if operation == "explain":
                yield self._doExplain(database)
            else:
                for data in compose(self._doSearchRetrieve(query, arguments)):
                    yield data
        except Exception, e:
            from traceback import print_exc
            print_exc()
            yield "Unexpected Exception:\n"
            yield str(e)
            raise e

    def _parseUri(self, RequestURI):
        Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
        ignored, database, command, ignored = (Path + '//').split('/', 3)
        arguments = parse_qs(Query)
        return database, command, arguments

    def _parseArguments(self, arguments):
        if arguments == {}:
            arguments = {'version':['1.1'], 'operation':['explain']}

        operation = arguments.get('operation', [None])[0]
        self._validateArguments(operation, arguments)
        return operation, arguments

    def _validateArguments(self, operation, arguments):
        if operation == None:
            raise SruException(MANDATORY_PARAMETER_NOT_SUPPLIED, 'operation')

        if not operation in SUPPORTED_OPERATIONS:
            raise SruException(UNSUPPORTED_OPERATION, operation)

        self._validateCorrectEncoding(arguments)

        for argument in arguments:
            if not (argument in OFFICIAL_REQUEST_PARAMETERS[operation] or argument.startswith('x-')):
                raise SruException(UNSUPPORTED_PARAMETER, argument)

        for argument in MANDATORY_PARAMETERS[operation]:
            if not argument in arguments:
                raise SruException(MANDATORY_PARAMETER_NOT_SUPPLIED, argument)

        if not arguments['version'][0] == VERSION:
            raise SruException(UNSUPPORTED_VERSION, arguments['version'][0])

    def _validateCorrectEncoding(self, arguments):
        try:
            for key, values in arguments.items():
                key.decode('utf-8')
                for value in values:
                    value.decode('utf-8')
        except UnicodeDecodeError:
            raise SruException(UNSUPPORTED_PARAMETER_VALUE, "Parameters are not properly 'utf-8' encoded.")

    def _doExplain(self, database):
        version = VERSION
        host = self._host
        port = self._port
        description = self._description
        modifiedDate = self._modifiedDate
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

    def _createSruQuery(self, arguments):
        try:
            sruQuery = SRUQuery(arguments, self._defaultRecordSchema, self._defaultRecordPacking)

            if self._maximumMaximumRecords and sruQuery.maximumRecords > self._maximumMaximumRecords:
                raise SruException(UNSUPPORTED_PARAMETER_VALUE, 'maximumRecords > %s' % self._maximumMaximumRecords)
        except SRUQueryParameterException, e:
            raise SruException(UNSUPPORTED_PARAMETER_VALUE, str(e))
        except SRUQueryParseException, e:
            raise SruException(QUERY_FEATURE_UNSUPPORTED, str(e))
        return sruQuery

    def _writeEchoedSearchRetrieveRequest(self, arguments):
        yield '<srw:echoedSearchRetrieveRequest>'
        for parameterName in ECHOED_PARAMETER_NAMES:
            for value in map(xmlEscape, arguments.get(parameterName, [])):
                yield '<srw:%(parameterName)s>%(value)s</srw:%(parameterName)s>' % locals()

        for chunk in decorate('<srw:extraRequestData>', compose(self.all.echoedExtraRequestData(arguments)), '</srw:extraRequestData>'):
            yield chunk
        yield '</srw:echoedSearchRetrieveRequest>'

    def _writeExtraResponseData(self, arguments, hits):
        return decorate('<srw:extraResponseData>',
            self._extraResponseDataTryExcept(arguments, hits),
            '</srw:extraResponseData>')

    def _extraResponseDataTryExcept(self, arguments, hits):
        try:
            stuffs = compose(self.all.extraResponseData(arguments, hits))
            for stuff in stuffs:
                yield stuff
        except Exception, e:
            yield DIAGNOSTIC % tuple(GENERAL_SYSTEM_ERROR + [xmlEscape(str(e))])

    def _doSearchRetrieve(self, sruQuery, arguments):
        SRU_IS_ONE_BASED = 1

        #KvS/TJ: volgende 'parseCQL(sruQuery.query)' is natuurlijk beetje jammer, volgende keer dat we hier langskomen: a. in sruquery dat resultaat opslaan en dan b. hier gebruiken.
        hits = self.any.executeCQL(parseCQL(sruQuery.query), sruQuery.sortBy,  sruQuery.sortDirection)
        yield self._startResults(len(hits))

        recordsWritten = 0
        start = sruQuery.startRecord - SRU_IS_ONE_BASED
        for recordId in hits[start: start + sruQuery.maximumRecords]:
            if not recordsWritten:
                yield '<srw:records>'
            yield self._writeResult(sruQuery, recordId)
            recordsWritten += 1

        if recordsWritten:
            yield '</srw:records>'
            nextRecordPosition = start + recordsWritten
            if nextRecordPosition < len(hits):
                yield '<srw:nextRecordPosition>%i</srw:nextRecordPosition>' % (nextRecordPosition + SRU_IS_ONE_BASED)

        yield self._writeEchoedSearchRetrieveRequest(arguments)
        yield self._writeExtraResponseData(arguments, hits)
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

        yield self._catchErrors(self.all.yieldRecordForRecordPacking(recordId, sruQuery.recordSchema, sruQuery.recordPacking))
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
            yield self._catchErrors(self.all.yieldRecordForRecordPacking(recordId, schema, sruQuery.recordPacking))
            yield '</recordData>'
        yield '</srw:extraRecordData>'

class PossibleXmlEscapeForRecordPacking(Observable):

    def unknown(self, msg, *args, **kwargs):
        return self.all.unknown(msg, *args, **kwargs)

    def yieldRecordForRecordPacking(self, recordId, recordSchema, recordPacking):
        generator = self.all.yieldRecord(recordId, recordSchema)
        if recordPacking == 'xml':
            for data in generator:
                yield data
        elif recordPacking == 'string':
            for data in generator:
                yield xmlEscape(data)
        else:
            raise Exception("Unknown Record Packing: %s" % recordPacking)
