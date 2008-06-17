
from cq2utils import CQ2TestCase, CallTrace

from meresco.components.http import PathFilter

class PathFilterTest(CQ2TestCase):
    def testSimplePath(self):
        f = PathFilter('/path')
        interceptor = CallTrace('Interceptor')
        f.addObserver(interceptor)
        list(f.handleRequest(RequestURI='/path', otherArgument='value'))
        self.assertEquals(1, len(interceptor.calledMethods))
        self.assertEquals('handleRequest', interceptor.calledMethods[0].name)
        self.assertEquals({'RequestURI':'/path', 'otherArgument':'value'}, interceptor.calledMethods[0].kwargs)

    def testOtherPath(self):
        f = PathFilter('/path')
        interceptor = CallTrace('Interceptor')
        f.addObserver(interceptor)
        list(f.handleRequest(RequestURI='/other/path'))
        self.assertEquals(0, len(interceptor.calledMethods))

    def testFullURL(self):
        f = PathFilter('/path')
        interceptor = CallTrace('Interceptor')
        f.addObserver(interceptor)
        list(f.handleRequest(RequestURI='http://example.org:8000/path?query=3#top'))
        self.assertEquals(1, len(interceptor.calledMethods))
        self.assertEquals('handleRequest', interceptor.calledMethods[0].name)
        self.assertEquals({'RequestURI':'http://example.org:8000/path?query=3#top'}, interceptor.calledMethods[0].kwargs)

    def testPaths(self):
        f = PathFilter(['/path', '/other/path'])
        interceptor = CallTrace('Interceptor')
        f.addObserver(interceptor)
        list(f.handleRequest(RequestURI='/other/path'))
        self.assertEquals(1, len(interceptor.calledMethods))

    def testExcludingPaths(self):
        f = PathFilter('/path', excluding=['/path/not/this'])
        interceptor = CallTrace('Interceptor')
        f.addObserver(interceptor)
        list(f.handleRequest(RequestURI='/path/not/this/path'))
        self.assertEquals(0, len(interceptor.calledMethods))
        list(f.handleRequest(RequestURI='/path/other'))
        self.assertEquals(1, len(interceptor.calledMethods))
