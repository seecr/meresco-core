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

import queryplugin
from amara import binderytools
from sruplugin import OFFICIAL_REQUEST_PARAMETERS, SRUPlugin
from cq2utils.amaraextension import getElements
from xml.sax.saxutils import escape as xmlEscape

UNSUPPORTED_PARAMETERS = ['stylesheet' ]
SOAP_XML_URI = "http://schemas.xmlsoap.org/soap/envelope/"

SOAP_VERSIONMISMATCH = """<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"><SOAP:Body><SOAP:Fault><faultcode>SOAP:VersionMismatch</faultcode><faultstring>The processing party found an invalid namespace for the SOAP Envelope element</faultstring></SOAP:Fault></SOAP:Body></SOAP:Envelope>"""

SOAP_JUNKMESSAGE="""<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"><SOAP:Body><SOAP:Fault><faultcode>SOAP:Server.userException</faultcode><faultstring>%s</faultstring></SOAP:Fault></SOAP:Body></SOAP:Envelope>"""

def registerOn(aRegistry):
    constructionMethod = lambda request,searchinterface: SRWPlugin(request, SRUPlugin(request, searchinterface))
    aRegistry.registerByCommand('srw', constructionMethod)

class SRWPlugin:
    
    def __init__(self, aRequest, aSRUPlugin):
        self._request = aRequest
        self._sruplugin = aSRUPlugin
        self._sruplugin.xmlHeader = ""
        self.contentType = 'text/xml; charset=utf-8'
        self._sruplugin._arguments = self.parseArguments(self._request.content.read())
        
        self._sruplugin.supportedOperation = self.supportedOperation
        self.sruSupportedParameter = self._sruplugin.supportedParameter
        self._sruplugin.supportedParameter = self.supportedParameter
    
    def __getattr__(self, attr):
        return getattr(self._sruplugin, attr)
    
    def __hasattr__(self, attr):
        return hasattr(self._sruplugin, attr)
    
    def parseArguments(self, data):
        arguments = {}
        try:
            envelope = binderytools.bind_string(data).Envelope
        except Exception, e:
            self.raiseException(SOAP_JUNKMESSAGE % xmlEscape(str(e)))
        if str(envelope.xmlnsUri) != SOAP_XML_URI:
            self.raiseException(SOAP_VERSIONMISMATCH)
        request = envelope.Body.searchRetrieveRequest
        for elem in getElements(request):
            value = arguments.get(str(elem.localName), [])
            value.append(str(elem))
            arguments[str(elem.localName)] = value
        arguments['operation'] = arguments.get('operation', ['searchRetrieve'])
        return arguments
    
    def process(self):
        self.write("""<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"><SOAP:Body>""")
        self._sruplugin.process()
        self.write("</SOAP:Body></SOAP:Envelope>")
        
    def supportedOperation(self, operation):
        return operation == 'searchRetrieve'

     def supportedParameter(self, parameter, operation):
         supported = self.sruSupportedParameter(parameter, operation)
         return supported and not parameter in UNSUPPORTED_PARAMETERS
        
