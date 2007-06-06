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
from amara import binderytools
from amara.bindery import is_element
from cStringIO import StringIO
import xml.dom
from cq2utils.component import Notification
from cq2utils.observable import Observable

class SRURecordUpdatePlugin(Observable):

	def _flattenXml(self, xml):
		return ''.join([child.xml() for child in xml.childNodes if is_element(child)])
	
	def notify(self, httpRequest):
		try:
			result = Notification()
			updateRequest = binderytools.bind_stream(httpRequest.content).updateRequest
			
			result.method = self.actionToMethod(updateRequest.action)
			result.id = str(updateRequest.recordIdentifier)
			if result.method == "add":
				result.partName = str(updateRequest.record.recordSchema)
				packing = updateRequest.record.recordPacking
				recordData = updateRequest.record.recordData
				if hasattr(updateRequest.record, "extraRecordData"):
					extraRecordData = updateRequest.record.extraRecordData
					result.extraRecordData = self._flattenXml(extraRecordData)
					self.interpretExtraRecordData(result, extraRecordData)
				if packing == 'text/plain':
					result.payload = str(recordData)
				elif packing == 'text/xml':
					result.payload = self._flattenXml(recordData)
				else:
					raise Exception("updateRequest.record.recordPacking should be either 'text/plain' or 'text/xml'.") 
	
			self.changed(result)
			self.writeSucces(httpRequest)
		except Exception, e:
			self.writeError(httpRequest, str(e))
			raise

	def actionToMethod(self, action):
		prefix = "info:srw/action/1/"
		if action == prefix + "replace" or action == prefix + "create":
			return "add"
		if action == prefix + "delete":
			return "delete"
		raise Exception("Unknown action: " + action)
	
	def interpretExtraRecordData(self, notification, extraRecordData):
		if hasattr(extraRecordData, "sets"):
			if hasattr(extraRecordData.sets, "set"):
				notification.sets = map(lambda set: (str(set.setSpec), str(set.setName)), extraRecordData.sets.set)
			else:
				notification.sets = []
	
	def writeSucces(self, httpRequest):
		response = RESPONSE_XML % {"operationStatus": "succes", "hook": ""}
		httpRequest.write(response)
		
	def writeError(self, httpRequest, message):
		response = RESPONSE_XML % {"operationStatus": "fail", "hook": DIAGNOSTIC_XML % message}
		httpRequest.write(response)
	
RESPONSE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<updateRequest xmlns:srw="info:srw/namespace/1/srw-schema" xmlns:ucp="info:srw/namespace/1/update">
	<srw:version>1.0</srw:version>
	<ucp:operationStatus>%(operationStatus)s</ucp:operationStatus>%(hook)s
</updateRequest>"""

DIAGNOSTIC_XML = """<srw:diagnostics>%s</srw:diagnostics>"""
