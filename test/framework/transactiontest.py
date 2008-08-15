
from cq2utils import CallTrace
from unittest import TestCase
from meresco.framework import TransactionFactory, be, Observable, compose, TransactionScope

class TransactionTest(TestCase):
    def testOne(self):
        traces = []
        def factoryMethod(tx):
            trace = CallTrace('transaction')
            traces.append(trace)
            return trace

        class CallTwoMethods(Observable):
            def twice(self, argument1, argument2):
                yield self.all.methodOne(argument1)
                yield self.all.methodTwo(argument2)
        
        dna = \
            (Observable(),
                (TransactionScope(),
                    (CallTwoMethods(),
                        (TransactionFactory(factoryMethod),)
                    )
                )
            )
        body = be(dna)

        list(compose(body.all.twice('one', 'two')))

        self.assertEquals(1, len(traces))
        self.assertEquals(3, len(traces[0].calledMethods))
        self.assertEquals(['methodOne', 'methodTwo', 'finalize'], [m.name for m in traces[0].calledMethods])

    def testTransactionFactoryHandlesAttributeError(self):
        methodsCalled = []
        class Mock(object):
            def finalize(self):
                methodsCalled.append('finalize')
            def exists(self):
                methodsCalled.append('exists')

        factory = TransactionFactory(lambda tx: Mock())
        __callstack_var_tx__ = CallTrace('Transaction')
        observable = Observable()
        observable.addObserver(factory)
        observable.once.begin()
        list(observable.all.exists())
        observable.once.commit()

        self.assertEquals(['exists', 'finalize'], methodsCalled)

        methodsCalled = []

        observable.once.begin()
        list(observable.all.doesNotExist())
        observable.once.commit()

        self.assertEquals(['finalize'], methodsCalled)





        