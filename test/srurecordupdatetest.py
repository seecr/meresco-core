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

from unittest import TestCase
from StringIO import StringIO

from cq2utils.calltrace import CallTrace

from meresco.components.http.srurecordupdateplugin import SRURecordUpdatePlugin


XML = """<?xml version="1.0" encoding="UTF-8"?>
<updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="http://www.loc.gov/KVS_IHAVENOIDEA/">
    <srw:version>1.0</srw:version>
    <ucp:action>info:srw/action/1/%(action)s</ucp:action>
    <ucp:recordIdentifier>%(recordIdentifier)s</ucp:recordIdentifier>
    <srw:record>
        <srw:recordPacking>%(recordPacking)s</srw:recordPacking>
        <srw:recordSchema>%(recordSchema)s</srw:recordSchema>
        <srw:recordData>%(recordData)s</srw:recordData>
        %(extraRecordData)s
    </srw:record>
</updateRequest>"""

XML_DOCUMENT = """<someXml>
with strings<nodes and="attributes"/>
</someXml>"""

TEXT_DOCUMENT = """Just some text"""

CREATE = "create"
REPLACE = "replace"
DELETE = "delete"

class SRURecordUpdatePluginTest(TestCase):
    """http://www.loc.gov/standards/sru/record-update/"""

    def setUp(self):
        self.subject = SRURecordUpdatePlugin()
        self.observer = CallTrace("Observer")
        self.subject.addObserver(self.observer)
        self.requestData = {
            "action": CREATE,
            "recordIdentifier": "defaultId",
            "recordPacking": "defaultPacking",
            "recordSchema": "defaultSchema",
            "recordData": "<defaultXml/>",
            "extraRecordData": ""}

    def createRequest(self):
        return MockHTTPRequest(XML % self.requestData)

    def testAddXML(self):
        self.requestData = {
            "action": "create",
            "recordIdentifier": "123",
            "recordPacking": "text/xml",
            "recordSchema": "irrelevantXML",
            "recordData": "<dc>empty</dc>",
            "extraRecordData": ""}
        self.subject.handleRequest(self.createRequest())
        self.assertEquals(1, len(self.observer.calledMethods))
        method = self.observer.calledMethods[0]
        self.assertEquals(3, len(method.arguments))
        self.assertEquals("add", method.name)
        self.assertEquals("123", method.arguments[0])
        self.assertEquals(str, type(method.arguments[0]))
        self.assertEquals("irrelevantXML", method.arguments[1])
        self.assertEquals("<dc>empty</dc>", method.arguments[2].xml())

    def testExtraRecordData(self):
        self.requestData["extraRecordData"] = "<srw:extraRecordData><one><a/></one><two/></srw:extraRecordData>"
        self.subject.handleRequest(self.createRequest())
        self.assertEquals(1, len(self.observer.calledMethods))
        method = self.observer.calledMethods[0]
        self.assertEquals(5, len(method.arguments), str(method))
        self.assertEquals("<one><a/></one>", method.arguments[3].xml())
        self.assertEquals("<two/>", method.arguments[4].xml())

    def testEmptyExtraRecordData(self):
        self.requestData["extraRecordData"] = "<srw:extraRecordData></srw:extraRecordData>"
        self.subject.handleRequest(self.createRequest())
        self.assertEquals(1, len(self.observer.calledMethods))

        method = self.observer.calledMethods[0]
        self.assertEquals(3, len(method.arguments), str(method))

    def testDelete(self):
        self.requestData["action"] = DELETE
        self.subject.handleRequest(self.createRequest())
        self.assertEquals(1, len(self.observer.calledMethods))

        method = self.observer.calledMethods[0]
        self.assertEquals("delete", method.name)

    def testReplaceIsAdd(self):
        self.requestData["action"] = REPLACE
        self.subject.handleRequest(self.createRequest())
        self.assertEquals(1, len(self.observer.calledMethods))

        method = self.observer.calledMethods[0]
        self.assertEquals("add", method.name)

    def testResponse(self):
        request = self.createRequest()
        self.subject.handleRequest(request)
        self.assertEquals(1, len(self.observer.calledMethods))

        self.assertTrue(request.written.find("""<ucp:operationStatus>succes</ucp:operationStatus>""") > -1)

    def testNotCorrectXml(self):
        request = MockHTTPRequest("nonsense")
        try:
            self.subject.handleRequest(request)
            self.fail()
        except Exception, e:
            self.assertEquals('SAXParseException', str(e.__class__).split('.')[-1])
        self.assertTrue(request.written.find("""<ucp:operationStatus>fail</ucp:operationStatus>""") > -1)

    def testErrorsArePassed(self):
        self.observer.exceptions['add'] = Exception('Some Exception')
        request = self.createRequest()
        try:
            self.subject.handleRequest(request)
            self.fail()
        except Exception, e:
            self.assertEquals('Some Exception', str(e))
        self.assertTrue(request.written.find("""<ucp:operationStatus>fail</ucp:operationStatus>""") > -1)
        self.assertTrue(request.written.find("""Some Exception""") > -1)


    def testAsHowItIsSupposedToBeUsed(self):
        self.requestData["extraRecordData"] = """"<srw:extraRecordData>
<oai:header xmlns:oai="http://www.openarchives.org/OAI/2.0/">
    <oai:identifier>12345</oai:identifier>
    <oai:datestamp>datestamp</oai:datestamp>
    <oai:setSpec>one</oai:setSpec>
    <oai:setSpec>two</oai:setSpec>
</oai:header></srw:extraRecordData>"""
        self.subject.handleRequest(self.createRequest())
        self.assertEquals(1, len(self.observer.calledMethods))
        method = self.observer.calledMethods[0]
        self.assertEquals("add", method.name)
        self.assertEquals(4, len(method.arguments))

        header = method.arguments[3]
        self.assertEquals('http://www.openarchives.org/OAI/2.0/', header.namespaceURI)
        self.assertEquals('header', header.localName)
        self.assertEquals(2, len(header.setSpec))

class MockHTTPRequest:

    def __init__(self, content):
        self.content = StringIO(content)
        self.written = ""

    def write(self, s):
        self.written += s
