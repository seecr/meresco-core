

from unittest import TestCase
from cq2utils import CallTrace
from meresco.components.lucene import String2CQL

class String2CQLTest(TestCase):
    def testOne(self):
        s = String2CQL()
        observer = CallTrace('observer')
        s.addObserver(observer)

        s.executeCQLString('term1')

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals(["CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('term1')))))"], [str(a) for a in observer.calledMethods[0].args])