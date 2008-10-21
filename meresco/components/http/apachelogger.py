
from meresco.framework import Transparant
from time import strftime, gmtime

class DevNull(object):
    def write(self, *args, **kwargs):
        pass
    def flush(self, *args, **kwargs):
        pass

logline = '%(ipaddress)s - %(user)s [%(timestamp)s] "%(Method)s %(path)s%(query)s HTTP/1.0" %(status)s %(responseSize)s "%(Referer)s" "%(UserAgent)s"\n'
class ApacheLogger(Transparant):
    def __init__(self, outputStream=DevNull()):
        Transparant.__init__(self)
        self._outputStream = outputStream
        
    def handleRequest(self, Method, Client, Headers, path, query='', *args, **kwargs):
        ipaddress = Client[0]
        timestamp = strftime('%d/%b/%Y:%H:%M:%S +0000', gmtime())
        responseSize = '??'
        user = '-'
        query = query and '?%s' % query or ''
        Referer = Headers.get('Referer', '-')
        UserAgent = Headers.get('User-Agent', '-')

        result = self.all.handleRequest(Method=Method, Client=Client, Headers=Headers, path=path, query=query, *args, **kwargs)

        status = 0
        for line in result:
            if not status and line.startswith('HTTP/1.0'):
                status = line[len('HTTP/1.0 '):][:3]
                self._outputStream.write(logline % locals())
                self._outputStream.flush()
            yield line
