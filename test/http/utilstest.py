import merescocore.components.http.utils as utils
from unittest import TestCase
from weightless import compose

class UtilsTest(TestCase):
    def testInsertHeader(self):

        def handleRequest(*args, **kwargs):
            yield  utils.okHtml
            yield '<ht'
            yield 'ml/>'

        newHeader = 'Set-Cookie: session=dummySessionId1234; path=/'
        result = ''.join(utils.insertHeader(handleRequest(), newHeader))
        header, body = result.split(utils.CRLF*2, 1)
        self.assertEquals('<html/>', body)
        headerParts = header.split(utils.CRLF)
        self.assertEquals("HTTP/1.0 200 OK", headerParts[0])
        self.assertTrue(newHeader in headerParts)
        self.assertTrue(utils.ContentTypeHtml in headerParts)