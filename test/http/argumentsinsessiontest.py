
from unittest import TestCase
from cq2utils import CallTrace
from meresco.components.http import ArgumentsInSession
from meresco.framework import Observable, compose

class ArgumentsInSessionTest(TestCase):
    def setUp(self):
        self.argsInSession = ArgumentsInSession()
        self.observer = CallTrace('Observer')
        self.argsInSession.addObserver(self.observer)
        
        
    def testAddOnlyOnce(self):
        sessions = []
        def handleRequest(session=None, *args, **kwargs):
            sessions.append(session)
            yield 'goodbye'
        self.observer.handleRequest = handleRequest

        session = {}
        list(compose(self.argsInSession.handleRequest(session=session, arguments={'aap': ["+'noot'"]})))
        self.assertEquals(['noot'], sessions[0]['aap'])
        self.assertEquals(session, sessions[0])
        
        list(compose(self.argsInSession.handleRequest(session=session, arguments={'aap': ["+'noot'"]})))
        self.assertEquals(sessions[0], sessions[1])
        self.assertEquals(['noot'], sessions[0]['aap'])

    def testParseAndSetSessionVars(self):
        arguments = {}
        def handleRequest(session=None, *args, **kwargs):
            arguments.update(session)
            yield 'goodbye'
        self.observer.handleRequest = handleRequest
        list(compose(self.argsInSession.handleRequest(session={}, arguments={'key': ["+('a simple tuple',)"]})))
        self.assertEquals(1, len(arguments))
        self.assertTrue('key' in arguments)
        self.assertEquals( [('a simple tuple',)], arguments['key'])

    def testParseAndSetAndRemoveSessionVars2(self):
        arguments = {}
        def handleRequest(session=None, *args, **kwargs):
            arguments.update(session)
            yield 'goodbye'
        self.observer.handleRequest = handleRequest
        session = {}
        list(compose(self.argsInSession.handleRequest(session=session, arguments={'aap': ["+'noot'"]})))
        self.assertEquals( ['noot'], arguments['aap'])
        list(compose(self.argsInSession.handleRequest(session=session, arguments={'aap': ["-'noot'"]})))
        self.assertEquals( [], arguments['aap'])

    def testDoNotEvalAnything(self):
        response = ''.join(compose(self.argsInSession.handleRequest(session={}, arguments={'key': ["+exit(0)"]})))
        self.assertEquals("HTTP/1.0 400 Bad Request\r\n\r\nname 'exit' is not defined", response)


