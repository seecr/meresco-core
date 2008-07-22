from cq2utils import CQ2TestCase, CallTrace

from meresco.components.http.observablehttpserver import ObservableHttpServer

class ObservableHttpServerTest(CQ2TestCase):
    def testSimpleHandleRequest(self):
        observer = CallTrace('Observer')
        s = ObservableHttpServer(CallTrace('Reactor'), 1024)
        s.addObserver(observer)

        list(s.handleRequest(RequestURI='http://localhost'))
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals('handleRequest', method.name)
        self.assertEquals(0, len(method.args))
        self.assertEquals(7, len(method.kwargs))
        
    def testHandleRequest(self):
        observer = CallTrace('Observer')
        s = ObservableHttpServer(CallTrace('Reactor'), 1024)
        s.addObserver(observer)

        list(s.handleRequest(RequestURI='http://localhost/path?key=value#fragment'))
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals('handleRequest', method.name)
        self.assertEquals(0, len(method.args))
        self.assertEquals(7, len(method.kwargs))
        self.assertTrue('arguments' in method.kwargs, method.kwargs)
        arguments = method.kwargs['arguments']
        self.assertEquals(1, len(arguments))
        self.assertEquals(['key'], arguments.keys())
        self.assertEquals(['value'], arguments['key'])
        