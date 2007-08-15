

from cq2utils.cq2testcase import CQ2TestCase

from cq2utils.calltrace import CallTrace
from meresco.framework.observable import Observable
from cStringIO import StringIO

from meresco.components.http.oai import OaiMain

class OaiMainTest(CQ2TestCase):
    
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.observable = Observable()
        self.subject = self.getSubject()
        self.subject.getTime = lambda : '2007-02-07T00:00:00Z'
        self.observable.addObserver(self.subject)
        self.request = CallTrace('Request')
        self.request.path = '/path/to/oai'
        self.request.getRequestHostname = lambda: 'server'
        class Host:
            def __init__(self):
                self.port = '9000'
        self.request.getHost = lambda: Host()
        self.stream = StringIO()
        self.request.write = self.stream.write

    def getSubject(self):
        return OaiMain()

    def testCallsUnknown(self):
        observer = Observer()
        self.subject.addObserver(observer)
        self.request.args = {'verb': ['SomeVerb']}
        
        self.observable.do.handleRequest(self.request)

        self.assertEquals('someVerb', observer.message)
        self.assertEquals(1, len(observer.args))
        self.assertTrue(self.request is observer.args[0])
    
    def testCallsUnknownWhenNoVerb(self):
        observer = Observer()
        self.subject.addObserver(observer)
        self.request.args = {}
        
        self.observable.do.handleRequest(self.request)

        self.assertEquals('', observer.message)
        self.assertEquals(1, len(observer.args))
        self.assertTrue(self.request is observer.args[0])

    def testCallFirstThingOnly(self):
        observer1 = Observer()
        observer2 = Observer()
        self.subject.addObservers([observer1, observer2])
        self.request.args = {'verb': ['SomeVerb']}
        usedargs=[]
        def someVerb(webrequest):
            usedargs.append(webrequest)
        observer1.someVerb = someVerb
        
        self.observable.do.handleRequest(self.request)

        self.assertEquals(1, len(usedargs))
        self.assertEquals(None, observer2.message)

        
class Observer(object):
    def __init__(self):
        self.message = None
        self.args = None
    def unknown(self, message, *args):
        self.message = message
        self.args = args
        yield None
