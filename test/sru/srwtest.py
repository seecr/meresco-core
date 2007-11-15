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

from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace

from meresco.components.sru.srw import Srw

soapEnvelope = '<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"><SOAP:Body>%s</SOAP:Body></SOAP:Envelope>'

echoedSearchRetrieveRequest = """<srw:echoedSearchRetrieveRequest>
<srw:version>1.1</srw:version>
<srw:query>%s</srw:query>
</srw:echoedSearchRetrieveRequest>"""

searchRetrieveResponse = """<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" xmlns:xcql="http://www.loc.gov/zing/cql/xcql/" xmlns:dc="http://purl.org/dc/elements/1.1/">\n<srw:version>1.1</srw:version><srw:numberOfRecords>%i</srw:numberOfRecords>%s</srw:searchRetrieveResponse>""" 

wrappedMockAnswer = searchRetrieveResponse % (1, '<srw:records><srw:record><srw:recordSchema>dc</srw:recordSchema><srw:recordPacking>xml</srw:recordPacking><srw:recordData><MOCKED_WRITTEN_DATA>0-dc</MOCKED_WRITTEN_DATA></srw:recordData></srw:record></srw:records>' + echoedSearchRetrieveRequest)

SRW_REQUEST = """<SRW:searchRetrieveRequest xmlns:SRW="http://www.loc.gov/zing/srw/">%s</SRW:searchRetrieveRequest>"""

argumentsWithMandatory = """<SRW:version>1.1</SRW:version><SRW:query>dc.author = "jones" and  dc.title = "smith"</SRW:query>%s"""

class SrwTest(CQ2TestCase):

    def testNonSoap(self):
        """Wrong Soap envelope or body"""
        invalidSoapEnvelope = '<?xml version="1.0"?><SOAP:Envelope xmlns:SOAP="http://wrong.example.org/soap/envelope/"><SOAP:Body>%s</SOAP:Body></SOAP:Envelope>'
        request = invalidSoapEnvelope % SRW_REQUEST % argumentsWithMandatory % ""

        response = "".join(list(Srw().handleRequest(self, Body=request)))
        self.assertEqualsWS("""<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"><SOAP:Body><SOAP:Fault><faultcode>SOAP:VersionMismatch</faultcode><faultstring>The processing party found an invalid namespace for the SOAP Envelope element</faultstring></SOAP:Fault></SOAP:Body></SOAP:Envelope>""", response)
        
        #TODO:
        #self.assertEquals(500, e.errorCode)
                
    def testMalformedXML(self):
        """Stuff that is not even XML"""
        request = 'This is not even XML'

        response = "".join(list(Srw().handleRequest(self, Body=request)))
        self.assertTrue('<faultcode>SOAP:Server.userException</faultcode>' in response)

    def testNonSRUArguments(self):
        """Arguments that are invalid in any SRU implementation"""
        request =  soapEnvelope % SRW_REQUEST % argumentsWithMandatory % """<SRW:illegalParameter>value</SRW:illegalParameter>"""
    
        response = "".join(list(Srw().handleRequest(self, Body=request)))
        
        self.assertEqualsWS(soapEnvelope % """<diagnostics><diagnostic xmlns="http://www.loc.gov/zing/srw/diagnostics/"><uri>info://srw/diagnostics/1/8</uri><details>illegalParameter</details><message>Unsupported Parameter</message></diagnostic></diagnostics>""", response)
    
    def testNonSRWArguments(self):
        """Arguments that are part of SRU, but not of SRW (operation (done), stylesheet)
        """
        request =  soapEnvelope % SRW_REQUEST % argumentsWithMandatory % """<SRW:stylesheet>http://example.org/style.xsl</SRW:stylesheet>"""
    
        response = "".join(list(Srw().handleRequest(self, Body=request)))
        
        self.assertEqualsWS(soapEnvelope % """<diagnostics><diagnostic xmlns="http://www.loc.gov/zing/srw/diagnostics/"><uri>info://srw/diagnostics/1/8</uri><details>stylesheet</details><message>Unsupported Parameter</message></diagnostic></diagnostics>""", response)
        
    
    def testOperationIsIllegal(self):
        request = soapEnvelope % SRW_REQUEST % """<SRW:version>1.1</SRW:version><SRW:operation>explain</SRW:operation>"""
        
        response = "".join(list(Srw().handleRequest(self, Body=request)))
        
        self.assertEqualsWS(soapEnvelope % """<diagnostics><diagnostic xmlns="http://www.loc.gov/zing/srw/diagnostics/"><uri>info://srw/diagnostics/1/4</uri><details>explain</details><message>Unsupported Operation</message></diagnostic></diagnostics>""", response)
    
    def xxxtestNonSupportedArguments(self):
        """Arguments that may be used in SRW but are illegal in a specific SRU subclass"""
        self.setupPluginWithRequest(soapEnvelope % SRW_REQUEST % argumentsWithMandatory % """<SRW:recordPacking>lom</SRW:recordPacking>""")
        
        self.plugin._sruplugin.supportedParameter = lambda param, oper: param != 'recordPacking'
        self.plugin.process()
        self.assertEqualsWS(soapEnvelope % """<diagnostics><diagnostic xmlns="http://www.loc.gov/zing/srw/diagnostics/"><uri>info://srw/diagnostics/1/8</uri><details>recordPacking</details><message>Unsupported Parameter</message></diagnostic></diagnostics>""", self.responseStream.getvalue())
    
    def xxxtestContentType(self):
        component = Srw()
        request = soapEnvelope % SRW_REQUEST % argumentsWithMandatory % ''
        response = "".join(list(component.handleRequest(self, Body=request)))
        self.assertTrue('text/xml; charset=utf-8' in response, response)

    
    def xxxtestExampleFromLibraryOffCongressSite(self):
        """Integration test based on http://www.loc.gov/standards/sru/srw/index.html
        spelling error ("recordSchema") corrected
        """
        self.setupPluginWithRequest("""<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/">
  <SOAP:Body>
    <SRW:searchRetrieveRequest xmlns:SRW="http://www.loc.gov/zing/srw/">
      <SRW:version>1.1</SRW:version>
      <SRW:query>dc.author = "jones" and  dc.title = "smith"</SRW:query>
      <SRW:startRecord>1</SRW:startRecord>
      <SRW:maximumRecords>10</SRW:maximumRecords>
      <SRW:recordSchema>info:srw/schema/1/mods-v3.0</SRW:recordSchema>
    </SRW:searchRetrieveRequest>
  </SOAP:Body>
</SOAP:Envelope>""")
        
        self.plugin.process()
        
        self.assertEquals(['searchRetrieve'], self.plugin._arguments['operation'])
        self.assertEquals(['1.1'], self.plugin._arguments['version'])
        self.assertEquals(['dc.author = "jones" and  dc.title = "smith"'], self.plugin._arguments['query'])
        self.assertEquals(['1'], self.plugin._arguments['startRecord'])
        self.assertEquals(['10'], self.plugin._arguments['maximumRecords'])
        self.assertEquals(['info:srw/schema/1/mods-v3.0'], self.plugin._arguments['recordSchema'])
        echoRequest = """<srw:echoedSearchRetrieveRequest>
<srw:version>1.1</srw:version>
<srw:query>dc.author = "jones" and  dc.title = "smith"</srw:query><srw:startRecord>1</srw:startRecord><srw:maximumRecords>10</srw:maximumRecords><srw:recordSchema>info:srw/schema/1/mods-v3.0</srw:recordSchema></srw:echoedSearchRetrieveRequest>"""
        
        self.assertEqualsWS(soapEnvelope % searchRetrieveResponse % (1, '<srw:records><srw:record><srw:recordSchema>info:srw/schema/1/mods-v3.0</srw:recordSchema><srw:recordPacking>xml</srw:recordPacking><srw:recordData><MOCKED_WRITTEN_DATA>0-info:srw/schema/1/mods-v3.0</MOCKED_WRITTEN_DATA></srw:recordData></srw:record></srw:records>' +echoRequest), self.responseStream.getvalue())
        
    def xxxtestNormalOperation(self):
        self.setupPluginWithRequest(soapEnvelope % SRW_REQUEST % argumentsWithMandatory % "")
        
        self.plugin.process()
        self.assertEquals(['searchRetrieve'], self.plugin._arguments['operation'])
        self.assertEquals(['1.1'], self.plugin._arguments['version'])
        self.assertEqualsWS(soapEnvelope % wrappedMockAnswer % 'dc.author = "jones" and  dc.title = "smith"', self.responseStream.getvalue())

    def xxxtestArgumentsAreNotUnicodeStrings(self):
        """JJ/TJ: unicode strings somehow paralyse server requests.
        So ensure every argument is a str!"""
        self.setupPluginWithRequest(soapEnvelope % SRW_REQUEST % argumentsWithMandatory % "")
        for key in self.plugin._arguments:
            self.assertTrue(type(key) == str)
            
    def xxxtestErrorInPluginShouldReturnAValidSRWResponse(self):
        self.setupPluginWithRequest(soapEnvelope % SRW_REQUEST % argumentsWithMandatory % "")
        self.plugin._sruplugin.doSearchRetrieve = lambda : 1/0
        self.plugin.process()
        self.assertEquals(['searchRetrieve'], self.plugin._arguments['operation'])
        self.assertEquals(['1.1'], self.plugin._arguments['version'])
        self.assertEqualsWS(soapEnvelope % searchRetrieveResponse % (0, """<diagnostics><diagnostic xmlns="http://www.loc.gov/zing/srw/diagnostics/">
        <uri>info://srw/diagnostics/1/1</uri>
        <details>integer division or modulo by zero</details>
        <message>General System Error</message>
        </diagnostic></diagnostics>"""), self.responseStream.getvalue())
    
