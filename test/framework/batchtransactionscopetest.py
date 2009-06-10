from cq2utils import CQ2TestCase, CallTrace
from merescocore.framework import BatchTransactionScope, Observable
from callstackscope import callstackscope

class BatchTransactionScopeTest(CQ2TestCase):
    def testOne(self):
        observer = CallTrace("observer")

        batchTransactionScope = BatchTransactionScope("batch", reactor=CallTrace("reactor"))
        batchTransactionScope.addObserver(observer)

        observable = Observable()
        observable.addObserver(batchTransactionScope)

        observable.do.exoticMethod()

        self.assertEquals(["begin", "exoticMethod"], [m.name for m in observer.calledMethods])

        
    def testBatchSize1(self):
        observable = Observable()
        batch = BatchTransactionScope("batch", reactor=CallTrace("reactor"), batchSize=1, timeout=99999999)
        observer = CallTrace('observer')
        committer = CallTrace("committer")
        def begin():
            tx = callstackscope('__callstack_var_tx__')
            tx.join(committer)
        observer.begin = begin
        observable.addObserver(batch)
        batch.addObserver(observer)

        observable.do.addDocument("aDocument")

        self.assertEquals(["addDocument"], [m.name for m in observer.calledMethods])
        self.assertEquals(['commit'], [m.name for m in committer.calledMethods])

    def testBatched(self):
        observable = Observable()
        batch = BatchTransactionScope("batch", reactor=CallTrace("reactor"), batchSize=2, timeout=99999999)
        observer = CallTrace('observer')
        committer = CallTrace("committer")
        def begin():
            tx = callstackscope('__callstack_var_tx__')
            tx.join(committer)
        observer.methods['begin'] = begin
        observable.addObserver(batch)
        batch.addObserver(observer)

        observable.do.addDocument("aDocument")

        self.assertEquals(['begin', "addDocument"], [m.name for m in observer.calledMethods])
        self.assertEquals([], [m.name for m in committer.calledMethods])

        observable.do.addDocument("aDocument")

        self.assertEquals(['begin', "addDocument", "addDocument"], [m.name for m in observer.calledMethods])
        self.assertEquals(["commit"], [m.name for m in committer.calledMethods])