from meresco.framework import Observable
from weightless import HttpServer
from cgi import parse_qs
from urlparse import urlsplit
from StringIO import StringIO
from socket import gethostname


class ObservableHttpServer(Observable):
    def __init__(self, reactor, port):
        Observable.__init__(self)
        self._port = port
        server = HttpServer(reactor, port, self._connect)

    def _connect(self, **kwargs):
        return self.all.handleRequest(port=self._port, **kwargs)

class WebRequest(object):
    def __init__(self, port=None, Client=None, RequestURI=None, Method=None, Headers=None, **kwargs):
        Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
        self.stream = StringIO()
        self.write = self.stream.write
        self.path = Path
        self.method = Method
        self.uri = RequestURI
        self.args = parse_qs(Query)
        self.received_headers = Headers
        self.client = self
        self.host = Client[0]
        self.headers = Headers
        host = self
        host.port = port
        self.getHost = lambda: host
        self.headersOut = {}
        self.responseCode = 200

    def getRequestHostName(self):
        return self.headers.get('Host', gethostname())

    def setResponseCode(self, code):
        self.responseCode = code

    def setHeader(self, key, value):
        self.headersOut['key'] = value

    def __str__(self):
        return '\t'.join((self.client.host, self.method, self.uri))

    def generateResponse(self):
        yield 'HTTP/1.0 %s Ok\r\n' % self.responseCode
        for key, value in self.headersOut.items():
            yield key.title() + ': ' + value + '\r\n'
        yield '\r\n'
        self.stream.seek(0)
        for line in self.stream.readlines():
            yield line

class ObservableHttpServerAdapter(Observable):

    def handleRequest(self,  **kwargs):
        webrequest = WebRequest(**kwargs)
        self.do.handleRequest(webrequest)
        return webrequest.generateResponse()