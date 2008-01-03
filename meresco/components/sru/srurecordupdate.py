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
from amara.binderytools import bind_stream
from amara.bindery import is_element
from meresco.framework.observable import Observable

class SRURecordUpdate(Observable):

    def handleRequest(self, httpRequest):
        try:
            updateRequest = bind_stream(httpRequest.content).updateRequest
            recordId = str(updateRequest.recordIdentifier)
            action = self.actionToMethod(str(updateRequest.action))
            record = updateRequest.record
            recordSchema = str(record.recordSchema)
            dataNodes = []
            dataNodes.append(record.recordData.childNodes[0])
            if hasattr(record, 'extraRecordData'):
                for child in record.extraRecordData.childNodes:
                    if is_element(child):
                        dataNodes.append(child)
            self.do.unknown(action, recordId, recordSchema, *dataNodes)
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

    def writeSucces(self, httpRequest):
        response = RESPONSE_XML % {
            "operationStatus": "succes",
            "diagnostics": ""}
        httpRequest.write(response)

    def writeError(self, httpRequest, message):
        response = RESPONSE_XML % {
            "operationStatus": "fail",
            "diagnostics": DIAGNOSTIC_XML % message}
        httpRequest.write(response)

RESPONSE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<updateRequest xmlns:srw="info:srw/namespace/1/srw-schema" xmlns:ucp="info:srw/namespace/1/update">
    <srw:version>1.0</srw:version>
    <ucp:operationStatus>%(operationStatus)s</ucp:operationStatus>%(diagnostics)s
</updateRequest>"""

DIAGNOSTIC_XML = """<srw:diagnostics>%s</srw:diagnostics>"""
