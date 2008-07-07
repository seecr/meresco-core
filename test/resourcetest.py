from unittest import TestCase
from cq2utils import CallTrace
from meresco.framework import Resource

class ResourceTest(TestCase):

    def testCreateResource(self):
        subject = CallTrace('subject')
        r = Resource(subject)
        self.assertEquals(0, len(subject.calledMethods))
        r.__del__()
        self.assertEquals('close', subject.calledMethods[0].name)

    def testCallOnDecRef(self):
        subject = CallTrace('subject')
        r = Resource(subject)
        self.assertEquals(0, len(subject.calledMethods))
        r = None
        self.assertEquals('close', subject.calledMethods[0].name)

    def testTransparentMethodCalls(self):
        subject = CallTrace('subject')
        r = Resource(subject)
        r.aap()
        self.assertEquals('aap', subject.calledMethods[0].name)