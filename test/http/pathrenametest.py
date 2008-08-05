from unittest import TestCase
from cq2utils import CallTrace
from meresco.components.http import PathRename
from meresco.framework import compose, Observable

class PathRenameTest(TestCase):
    def testRename(self):
        rename = PathRename(lambda path: '/new'+path)
        interceptor = CallTrace('interceptor')
        rename.addObserver(interceptor)

        list(compose(rename.handleRequest(path='/mypath')))

        self.assertEquals(1, len(interceptor.calledMethods))
        self.assertEquals("handleRequest(path='/new/mypath')", str(interceptor.calledMethods[0]))

    def testTransparency(self):
        observable = Observable()
        rename = PathRename(lambda path: '/new'+path)
        interceptor = CallTrace('interceptor')
        observable.addObserver(rename)
        rename.addObserver(interceptor)

        observable.do.otherMethod('attribute')

        self.assertEquals(1, len(interceptor.calledMethods))
        self.assertEquals("otherMethod('attribute')", str(interceptor.calledMethods[0]))
