
from cq2utils import CQ2TestCase, CallTrace

from merescocore.components.http import HandleRequestFilter
from merescocore.framework import be, Observable

class HandleRequestFilterTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.observer = CallTrace('Observer')

        self.usedKwargs = []
        def filterMethod(**kwargs):
            self.usedKwargs.append(kwargs)
            return self.result

        self.dna = be(
            (Observable(),
                (HandleRequestFilter(filterMethod),
                    (self.observer, )
                )
            )
        )

        
    def testPasses(self):
        self.result = True
        inputKwargs = dict(path='path', Method='GET')
        list(self.dna.all.handleRequest(**inputKwargs))

        self.assertEquals([('handleRequest', inputKwargs)], [(m.name, m.kwargs) for m in self.observer.calledMethods])
        self.assertEquals([inputKwargs], self.usedKwargs)

    def testYouShallNotPass(self):
        """Fly you fools!"""
        self.result = False
        inputKwargs = dict(path='path', Method='GET')
        list(self.dna.all.handleRequest(**inputKwargs))

        self.assertEquals([], [m.name for m in self.observer.calledMethods])
        self.assertEquals([inputKwargs], self.usedKwargs)
