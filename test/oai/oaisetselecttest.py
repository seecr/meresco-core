from cq2utils import CQ2TestCase, CallTrace

from meresco.framework import be, Observable
from meresco.components.oai import OaiSetSelect

class OaiSetSelectTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.observer = CallTrace()

        self.dna = be(
            (Observable(),
                (OaiSetSelect(['set1', 'set2']),
                    (self.observer,)
                )
            )
        )

    def testOne(self):
        list(self.dna.all.oaiSelect())
        self.assertEquals(1, len(self.observer.calledMethods))
        methodCalled = self.observer.calledMethods[0]
        self.assertTrue('sets' in methodCalled.kwargs, methodCalled)
        self.assertEquals(['set1', 'set2'], self.observer.calledMethods[0].kwargs['sets'])

    def testOtherMethodsArePassed(self):
        list(self.dna.all.getAllPrefixes())
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals('getAllPrefixes', self.observer.calledMethods[0].name)

    def testSetsIsNone(self):
        list(self.dna.all.oaiSelect(sets=None))
        self.assertEquals(1, len(self.observer.calledMethods))
        methodCalled = self.observer.calledMethods[0]
        self.assertTrue('sets' in methodCalled.kwargs, methodCalled)
        self.assertEquals(['set1', 'set2'], self.observer.calledMethods[0].kwargs['sets'])
        