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

import os
from xml.sax.saxutils import escape as xmlEscape
from sruquery import SRUQuery, SRUQueryParameterException, SRUQueryParseException

from cq2utils.observable import Observable
import queryplugin

VERSION = '1.1'

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


class SRUDiagnostic(Exception):
	def __init__(self, diagnostic):
		Exception.__init__(self, str(diagnostic))
		self.diagnostic = diagnostic

class SRUPlugin(queryplugin.QueryPlugin, Observable):
	#current status: not supporting pure plugin behavior - is really an observable
	#refactor direction: remove queryplugin.QueryPlugin
	
	def __init__(self, aRequest, searchInterface):
		queryplugin.QueryPlugin.__init__(self, aRequest, searchInterface)
		Observable.__init__(self)
	
	def initialize(self):
		self.xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>'
		self.responseHeader = RESPONSE_HEADER
		self.contentType = 'text/xml; charset=utf-8'
		if self._arguments == {}:
			self._arguments = self.default_arguments()
	
	def default_arguments(self):
		return {'version':['1.1'], 'operation':['explain']}
	
	def validate(self):
		operation = self.getOperation()
		if operation == None:
			return MANDATORY_PARAMETER_NOT_SUPPLIED + ['operation']
	
		if not self.supportedOperation(operation):
			return UNSUPPORTED_OPERATION + [operation]
		
		for key in self._arguments:
			if not (self.supportedParameter(key, operation) or key.startswith('x-')):
				return UNSUPPORTED_PARAMETER + [key]

		for key in MANDATORY_PARAMETERS[operation]:
			if not key in self._arguments:
				return MANDATORY_PARAMETER_NOT_SUPPLIED + [key]

		if not self._arguments['version'][0] == VERSION:
			return UNSUPPORTED_VERSION + [self._arguments['version'][0]]
		
		if operation == 'searchRetrieve':
			return self._validateSearchRetrieve()
		
		return SUCCESS
		
	def _validateSearchRetrieve(self):
		try:
			self.sruquery = SRUQuery(self._database, self._arguments)
		except SRUQueryParameterException, e:
			return UNSUPPORTED_PARAMETER_VALUE + [str(e)]
		except SRUQueryParseException, e:
			return QUERY_FEATURE_UNSUPPORTED + [str(e)]
		return SUCCESS

	def getOperation(self):
		return self._arguments.get('operation', [None])[0]
			
	def _startResults(self, numberOfRecords):
		self.write(self.responseHeader)
		self.write('<srw:version>%s</srw:version>' % VERSION)
		self.write('<srw:numberOfRecords>%s</srw:numberOfRecords>' % numberOfRecords)
	
	def _endResults(self):
		self.write(RESPONSE_FOOTER)
		
	def _writeResult(self, aRecord):
		self.write('<srw:record>')
		self.write('<srw:recordSchema>%s</srw:recordSchema>' % self.sruquery.recordSchema)
		self.write('<srw:recordPacking>%s</srw:recordPacking>' % self.sruquery.recordPacking)
		self._writeRecordData(aRecord)
		self._writeExtraRecordData(aRecord)
		self.write('</srw:record>')

	def writeErrorDiagnosticsResponse(self, aList):
		self.write(self.responseHeader)
		self.write('<srw:version>%s</srw:version>' % VERSION)
		self.write('<srw:numberOfRecords>0</srw:numberOfRecords>')
		self.writeErrorDiagnostics(aList)
		self.write(RESPONSE_FOOTER)

	def writeErrorDiagnostics(self, aList):
		number = aList[0]
		message = aList[1]
		details = len(aList) >= 3 and aList[2] or "No details available"
		self.write(DIAGNOSTICS % (number, xmlEscape(details), message))
	
	def _writeRecordData(self, aRecord):
		self.write('<srw:recordData>')
		aRecord.writeDataOn(self.sruquery.recordSchema, self)
		self.write('</srw:recordData>')

	def _writeExtraRecordData(self, aRecord):
		if not self.sruquery.x_recordSchema:
			return
		self.write('<srw:extraRecordData>')
		for schema in self.sruquery.x_recordSchema:
			self.write('<recordData recordSchema="%s">' % xmlEscape(schema))
			aRecord.writeDataOn(schema, self)
			self.write('</recordData>')
		self.write('</srw:extraRecordData>')

	def _writeExtraResponseData(self, aSearchResult):
		self.write('<srw:extraResponseData>')
		aSearchResult.writeExtraResponseDataOn(self) #refactor direction: push down to observers
		self.all.writeExtraResponseData(self)
		self.write('</srw:extraResponseData>')

	def doSearchRetrieve(self):
		searchResult = self.searchInterface.search(self.sruquery)
		
		self._startResults(searchResult.getNumberOfRecords())
		
		recordstag = '<srw:records>'
		for record in searchResult.getRecords():
			self.write(recordstag)
			self._writeResult(record)
			recordstag = ''
			
		if recordstag == '':
			self.write('</srw:records>')
			nextRecordPosition = searchResult.getNextRecordPosition()
			if nextRecordPosition:
				self.write('<srw:nextRecordPosition>%i</srw:nextRecordPosition>' % nextRecordPosition)
		
		self._writeEchoedSearchRetrieveRequest()
		self._writeExtraResponseData(searchResult)

		self._endResults()
	
	def _writeEchoedSearchRetrieveRequest(self):
		self.write('<srw:echoedSearchRetrieveRequest>')
		for parameterName in ECHOED_PARAMETER_NAMES:
			for value in map(xmlEscape, self._arguments.get(parameterName, [])):
				self.write('<srw:%(parameterName)s>%(value)s</srw:%(parameterName)s>' % locals())
		self._writeEchoedExtraRequestData()
		self.write('</srw:echoedSearchRetrieveRequest>')
		
	def _writeEchoedExtraRequestData(self):
		"""Write extra request data like drilldown parameters. Not used yet."""
		pass
	
	def doExplain(self):
		version = VERSION
		host = self.getenv('server.host')
		port = self.getenv('server.port')
		database = self._database
		description = self.getenv('server.description')
		modifiedDate = self.getenv('server.modifieddate')
		self.write("""
<srw:explainResponse xmlns:srw="http://www.loc.gov/zing/srw/"
   xmlns:zr="http://explain.z3950.org/dtd/2.0/">
	<srw:version>%(version)s</srw:version>
	<srw:record>
		<srw:recordPacking>XML</srw:recordPacking>  
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
</srw:explainResponse>""" % locals())
		
	def process(self):
		self.write(self.xmlHeader)
		errorMethod = self.writeErrorDiagnostics
		try:
			code = self.validate()
			if code == SUCCESS:
				operation = self.getOperation()
				if operation == 'explain':
					return self.doExplain()
				errorMethod = self.writeErrorDiagnosticsResponse
				self.doSearchRetrieve()
			else:
				errorMethod(code)
		except KeyboardInterrupt:
			errorMethod(SYSTEM_TEMPORARILY_UNAVAILABLE)
		except Exception, e:
			self.logException()
			errorMethod(GENERAL_SYSTEM_ERROR + [str(e)])
	
	def supportedOperation(self, operation):
		return operation in SUPPORTED_OPERATIONS
	
	def supportedParameter(self, parameterName, operation):
		return parameterName in OFFICIAL_REQUEST_PARAMETERS[operation]



def registerOn(aRegistry):
	aRegistry.registerByCommand('sru', SRUPlugin)
