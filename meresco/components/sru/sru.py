from cgi import parse_qs
from urlparse import urlsplit
from xml.sax.saxutils import escape as xmlEscape

from meresco.framework import Observable, decorate, compose
from meresco.legacy.plugins.sruquery import SRUQuery, SRUQueryParameterException, SRUQueryParseException

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

DIAGNOSTICS = """<diagnostics>
  <diagnostic xmlns="http://www.loc.gov/zing/srw/diagnostics/">
        <uri>info://srw/diagnostics/1/%s</uri>
        <details>%s</details>
        <message>%s</message>
    </diagnostic>
</diagnostics>
"""

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
    """CAUTION: dit object zuigt langzaam de code over van de sruplugin.py. Idee is dat op termaijn alles is overgenomen in het nieuwe format, en dat je deze dan rechtstreeks in de boom kan hangen. Nog niet alles zit er nu echter in... dus het kan nu nog niet."""

    def __init__(self, host, port, description, modifiedDate, defaultRecordSchema="dc", defaultRecordPacking="xml", maximumMaximumRecords=None):
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
        yield XML_HEADER
        try:
            operation, arguments = self._parseArguments(queryArguments)
            if operation == "explain":
                yield self._doExplain(database)
            else:
                query = self._createSruQuery(arguments)
                for data in compose(self._doSearchRetrieve(query, arguments)):
                    yield data
        except SruException, e:
            yield DIAGNOSTICS % (e.code, xmlEscape(e.details), xmlEscape(e.message))

    def _parseUri(self, RequestURI):
        Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
        ignored, database, command, ignored = (Path + '//').split('/', 3)
        arguments = parse_qs(Query)
        return database, command, arguments

    def _parseArguments(self, arguments):
        if arguments == {}:
            arguments = {'version':['1.1'], 'operation':['explain']}

        operation = arguments.get('operation', [None])[0]

        if operation == None:
            raise SruException(MANDATORY_PARAMETER_NOT_SUPPLIED, 'operation')

        if not operation in SUPPORTED_OPERATIONS:
            raise SruException(UNSUPPORTED_OPERATION, operation)

        for argument in arguments:
            if not (argument in OFFICIAL_REQUEST_PARAMETERS[operation] or argument.startswith('x-')):
                raise SruException(UNSUPPORTED_PARAMETER, argument)

        for argument in MANDATORY_PARAMETERS[operation]:
            if not argument in arguments:
                raise SruException(MANDATORY_PARAMETER_NOT_SUPPLIED, argument)

        if not arguments['version'][0] == VERSION:
            raise SruException(UNSUPPORTED_VERSION, arguments['version'][0])

        return operation, arguments

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
        openingTagWritten = False
        extraResponses = self.all.extraResponseData(arguments, hits)
        for response in extraResponses:
            if not response:
                continue
            if not openingTagWritten:
                yield '<srw:extraResponseData>'
                openingTagWritten = True
            for line in response:
                yield line
        if openingTagWritten:
            yield '</srw:extraResponseData>'

    def _doSearchRetrieve(self, sruQuery, arguments):
        SRU_IS_ONE_BASED = 1

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
        yield self.all.writeRecord(recordId, sruQuery.recordSchema, sruQuery.recordPacking)
        yield '</srw:recordData>'

    def _writeExtraRecordData(self, sruQuery, recordId):
        if not sruQuery.x_recordSchema:
            yield ''

        yield '<srw:extraRecordData>'
        for schema in sruQuery.x_recordSchema:
            yield '<recordData recordSchema="%s">' % xmlEscape(schema)
            yield self.all.writeRecord(recordId, schema, sruQuery.recordPacking)
            yield '</recordData>'
        yield '</srw:extraRecordData>'
#NOG TE DOEN:
#eerdere aanroep was self.all.extraResponseData(SELF, hits). luisteraars aanpassen
#idem voor
#self.do.writeRecord(self, recordId, self.sruQuery.recordSchema, self.sruQuery.recordPacking)
#en die naam is ook niet zo fris meer
