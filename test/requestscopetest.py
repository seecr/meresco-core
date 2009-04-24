
from cq2utils import CQ2TestCase
from merescocore.framework import Observable
from merescocore.components import RequestScope

class RequestScopeTest(CQ2TestCase):
    def testEverythingIsPassed(self):
        usedArgsKwargs=[]
        class MyObserver(Observable):
            def handleRequest(innerself, *args, **kwargs):
                usedArgsKwargs.append((args, kwargs))
                yield 'result'
        r = RequestScope()
        r.addObserver(MyObserver())

        result = list(r.handleRequest("an arg", RequestURI='http://www.example.org/path'))

        self.assertEquals(['result'], result)
        self.assertEquals([(("an arg",), dict(RequestURI='http://www.example.org/path'))], usedArgsKwargs)

    def testRequestScopeIsAvailable(self):
        class MyObserver(Observable):
            def handleRequest(self, *args, **kwargs):
                self.do.setArg()
                yield self.any.getArg()
        class SetArgObserver(Observable):
            def setArg(self):
                self.requestScope["arg"] = "value"
        class GetArgObserver(Observable):
            def getArg(self):
                return self.requestScope["arg"]

        r = RequestScope()
        myObserver = MyObserver()
        myObserver.addObserver(SetArgObserver())
        myObserver.addObserver(GetArgObserver())
        r.addObserver(myObserver)

        result = list(r.handleRequest("a request"))

        self.assertEquals(['value'], result)

    def testRequestScopeIsPerRequest(self):
        class MyObserver(Observable):
            def handleRequest(self, key, value, *args, **kwargs):
                self.do.setArg(key, value)
                yield self.any.getArg()
        class SetArgObserver(Observable):
            def setArg(self, key, value):
                self.requestScope[key] = value
        class GetArgObserver(Observable):
            def getArg(self):
                return ';'.join('%s=%s' % (k,v) for k,v in self.requestScope.items())

        r = RequestScope()
        myObserver = MyObserver()
        myObserver.addObserver(SetArgObserver())
        myObserver.addObserver(GetArgObserver())
        r.addObserver(myObserver)

        result0 = list(r.handleRequest("key0", "value0"))
        result1 = list(r.handleRequest("key1", "value1"))

        self.assertEquals(['key0=value0'], result0)
        self.assertEquals(['key1=value1'], result1)
        
