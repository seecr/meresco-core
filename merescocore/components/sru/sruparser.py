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

class SruParser(Observable):

    def __init__(self, host='', port=0, description='Meresco SRU', modifiedDate='1970-01-01T00:00:00Z', database=None, defaultRecordSchema="dc", defaultRecordPacking="xml", maximumMaximumRecords=None):
        Observable.__init__(self)
        self._host = host
        self._port = port
        self._description = description
        self._modifiedDate = modifiedDate
        self._database = database
        self._defaultRecordSchema = defaultRecordSchema
        self._defaultRecordPacking = defaultRecordPacking
        self._maximumMaximumRecords = maximumMaximumRecords

    def handleRequest(self, arguments, **kwargs):
        operations = {
            'searchRetrieve': self._searchRetrieve,
            'explain': self._explain
        }
        yield httputils.okXml

        yield XML_HEADER
        try:
            operation, arguments = self._parseArguments(arguments)
            if not operation in operations:
                raise something

            for data in operations[operation](arguments):
                yield data
        except SruException, e:
            yield DIAGNOSTICS % (e.code, xmlEscape(e.details), xmlEscape(e.message))
            raise StopIteration()
        except Exception, e:
            from traceback import print_exc
            print_exc()
            yield "Unexpected Exception:\n"
            yield str(e)
            raise e

    def _searchRetrieve(self, arguments):
        sruQuery = self._createSruQuery(arguments)
        return self.any.searchRetrieve(sruQuery=sruQuery,**arguments)

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

    def _explain(self, *args, **kwargs):
        version = VERSION
        host = self._host
        port = self._port
        description = self._description
        modifiedDate = self._modifiedDate
        database = self._database
        yield """<srw:explainResponse xmlns:srw="http://www.loc.gov/zing/srw/"
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
