from cgi import parse_qs
from urlparse import urlsplit


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

SUCCESS = [0, ""]
GENERAL_SYSTEM_ERROR = [1, "General System Error"]
SYSTEM_TEMPORARILY_UNAVAILABLE = [2, "System Temporarily Unavailable"]
UNSUPPORTED_OPERATION = [4, "Unsupported Operation"]
UNSUPPORTED_VERSION = [5, "Unsupported Version"]
UNSUPPORTED_PARAMETER_VALUE = [6, "Unsupported Parameter Value"]
MANDATORY_PARAMETER_NOT_SUPPLIED = [7, "Mandatory Parameter Not Supplied"]
UNSUPPORTED_PARAMETER = [8, "Unsupported Parameter"]
QUERY_FEATURE_UNSUPPORTED = [48, "Query Feature Unsupported"]

class Sru(object):
    """CAUTION: dit object zuigt langzaam de code over van de sruplugin.py. Idee is dat op termaijn alles is overgenomen in het nieuwe format, en dat je deze dan rechtstreeks in de boom kan hangen. Nog niet alles zit er nu echter in... dus het kan nu nog niet."""

    def __init__(self, host, port, description, modifiedDate):
        self._host = host
        self._port = port
        self._description = description
        self._modifiedDate = modifiedDate

    def handleRequest(self, port=None, Client=None, RequestURI=None, Method=None, Headers=None, **kwargs):
        database, command, arguments = self._parseUri(RequestURI)
        if arguments == {}:
            arguments = {'version':['1.1'], 'operation':['explain']}

        operation = checkNotUtterGarbage()
        if explian:
            yield explain()
        else:
            someMoreChecks()
            query = parseQuery()
            yield self.doSearchRetrieve()

        yield XML_HEADER
        yield self.doExplain(database)

    def _parseUri(self, RequestURI):
        Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
        ignored, database, command, ignored = (Path + '//').split('/', 3)
        arguments = parse_qs(Query)
        return database, command, arguments

    def _basicValidation(self, arguments):
        operation = arguments.get('operation', [None])[0]

        if operation == None:
            return MANDATORY_PARAMETER_NOT_SUPPLIED + ['operation']

        if not operation in SUPPORTED_OPERATIONS:
            return UNSUPPORTED_OPERATION + [operation]

        for argument in arguments:
            if not (argument in OFFICIAL_REQUEST_PARAMETERS[operation] or argument.startswith('x-')):
                return UNSUPPORTED_PARAMETER + [argument]

        for argument in MANDATORY_PARAMETERS[operation]:
            if not argument in arguments:
                return MANDATORY_PARAMETER_NOT_SUPPLIED + [argument]

        if not arguments['version'][0] == VERSION:
            return UNSUPPORTED_VERSION + [arguments['version'][0]]

        return SUCCESS

    def _validateSearchRetrieve(self, arguments):
        #try:
            #dit is ellende:
            #self.sruQuery = SRUQuery(self._arguments, self.recordSchema, self.recordPacking)

            #nog niet getest
        #if self.sruQuery.maximumRecords > 100:
            #return UNSUPPORTED_PARAMETER_VALUE + ['maximumRecords > %s' % 100]
        #except SRUQueryParameterException, e:
            #return UNSUPPORTED_PARAMETER_VALUE + [str(e)]
        #except SRUQueryParseException, e:
            #return QUERY_FEATURE_UNSUPPORTED + [str(e)]
        return SUCCESS

    def doExplain(self, database):
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
