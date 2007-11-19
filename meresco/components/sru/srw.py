## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school.
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

from xml.sax.saxutils import escape as xmlEscape
from amara.binderytools import bind_string

from cq2utils.amaraextension import getElements
from meresco.framework import Observable, compose

SOAP_XML_URI = "http://schemas.xmlsoap.org/soap/envelope/"

SOAP_HEADER = """<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"><SOAP:Body>"""

SOAP_FOOTER = """</SOAP:Body></SOAP:Envelope>"""

SOAP = SOAP_HEADER + "%s" + SOAP_FOOTER

from meresco.components.sru import Sru
from meresco.components.sru.sru import SruException, DIAGNOSTICS, UNSUPPORTED_PARAMETER, UNSUPPORTED_OPERATION

class SoapException(Exception):

    def __init__(self, faultCode, faultString):
        self._faultCode = faultCode
        self._faultString = faultString

    def asSoap(self):
        return """<SOAP:Fault><faultcode>%s</faultcode><faultstring>%s</faultstring></SOAP:Fault>""" % (xmlEscape(self._faultCode), xmlEscape(self._faultString))

class Srw(Observable):

    def __init__(self, **kwargs):
        Observable.__init__(self)
        ignored = "SRW Does Not Implement Explain - This Variable Will Not Be Used"
        self._sruDelegate = Sru(host=ignored, port=ignored, description=ignored, modifiedDate=ignored, **kwargs)
        self._sruDelegate.all = self.all
        self._sruDelegate.any = self.any
        self._sruDelegate.do = self.do

    def handleRequest(self, Body='', **kwargs):
        try:
            arguments = self._soapXmlToArguments(Body)
        except SoapException, e:
            #yield http.Response.Status_Line(500)
            #yield http.Response.Content_Type('text/xml; charset=utf-8')
            yield "HTTP/1.0 500 Internal Server Error\r\n" + \
                "Content-Type: text/xml; charset=utf-8\r\n" + \
                "\r\n"
            yield SOAP % e.asSoap()
            raise StopIteration()

        yield "HTTP/1.0 200 Ok\r\n" + \
              "Content-Type: text/xml; charset=utf-8\r\n" + \
              "\r\n"
        try:
            operation, arguments = self._sruDelegate._parseArguments(arguments)
            self._srwSpecificValidation(operation, arguments)
            query = self._sruDelegate._createSruQuery(arguments)
        except SruException, e:
            yield SOAP % DIAGNOSTICS % (e.code, xmlEscape(e.details), xmlEscape(e.message))
            raise StopIteration()

        try:
            yield SOAP_HEADER
            for data in compose(self._sruDelegate._doSearchRetrieve(query, arguments)):
                yield data
            yield SOAP_FOOTER
        except Exception, e:
            yield "Unexpected Exception:\n"
            yield str(e)
            raise e

    def _soapXmlToArguments(self, body):
        arguments = {}
        try:
            envelope = bind_string(body).Envelope
        except Exception, e:
            raise  SoapException("SOAP:Server.userException", str(e))
        if str(envelope.xmlnsUri) != SOAP_XML_URI:
            raise SoapException("SOAP:VersionMismatch", "The processing party found an invalid namespace for the SOAP Envelope element")

        request = envelope.Body.searchRetrieveRequest
        for elem in getElements(request):
            value = arguments.get(str(elem.localName), [])
            value.append(str(elem))
            arguments[str(elem.localName)] = value
        arguments['operation'] = arguments.get('operation', ['searchRetrieve'])
        return arguments

    def _srwSpecificValidation(self, operation, arguments):
        if operation != 'searchRetrieve':
            raise SruException(UNSUPPORTED_OPERATION, operation)
        if 'stylesheet' in arguments:
            raise SruException(UNSUPPORTED_PARAMETER, 'stylesheet')

