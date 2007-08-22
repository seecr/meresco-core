
from meresco.components.oai.resumptiontoken import ResumptionToken, resumptionTokenFromString
from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace

class ResumptionTokenTest(CQ2TestCase):
    def assertResumptionToken(self, token):
        aTokenString = str(token)
        token2 = resumptionTokenFromString(aTokenString)
        self.assertEquals(token, token2)
    
    def testResumptionToken(self):
        self.assertResumptionToken(ResumptionToken())
        self.assertResumptionToken(ResumptionToken('oai:dc', '100', '2002-06-01T19:20:30Z', '2002-06-01T19:20:39Z', 'some:set:name'))
        self.assertResumptionToken(ResumptionToken(_set=None))

    
