## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import sys
from traceback import format_tb
from types import GeneratorType

from meresco.framework import Observable, TransactionScope, Transparant
from meresco.framework.observable import be
from cq2utils.calltrace import CallTrace
import unittest

class Interceptor(Observable):
    def unknown(self, message, *args, **kwargs):
        self.message = message
        self.args = args
        self.kwargs = kwargs

class ObservableTest(unittest.TestCase):

    def testObserverInit(self):
        initcalled = [0]
        class MyObserver(object):
            def observer_init(self):
                initcalled[0] += 1
        root = be((Observable(), (MyObserver(),)))
        root.once.observer_init()
        self.assertEquals([1], initcalled)

    def testAllWithoutImplementers(self):
        observable = Observable()
        responses = observable.all.someMethodNobodyIsListeningTo()
        self.assertEquals(GeneratorType, type(responses))

    def testAllWithMoreImplementers(self):
        observable = Observable()
        observerOne = CallTrace(returnValues={'aMethod': 'one'})
        observerTwo = CallTrace(returnValues={'aMethod': 'two'})
        root = be((observable, (observerOne,), (observerTwo,)))
        responses = root.all.aMethod()
        self.assertEquals(GeneratorType, type(responses))
        self.assertEquals(['one', 'two'], list(responses))

    def testAnyCallsFirstImplementer(self):
        observable = Observable()
        observerA = ObserverA()
        observerAB = ObserverAB()
        root = be((observable, (observerA,), (observerAB,)))
        resultA = root.any.methodA(0)
        resultB = root.any.methodB(1, 2)
        self.assertEquals([("Method A", (0,))], observerA.notifications)
        self.assertEquals([("Method B", (1, 2))], observerAB.notifications)
        self.assertEquals("A.methodA", resultA)
        self.assertEquals("AB.methodB", resultB)

    def testAllException(self):
        observable = Observable()
        class ExceptionRaiser(MockObserver):
            def mayRaiseException(self, *args):
                raise TestException
        class Safe(MockObserver):
            def mayRaiseException(self, *args):
                self.notifications.append(("mayRaiseException", args))
        observable.addObserver(ExceptionRaiser())
        safe = Safe()
        observable.addObserver(safe)
        try:
            list(observable.all.mayRaiseException())
            self.fail()
        except TestException:
            pass
        self.assertEquals([], safe.notifications)

    def testDo(self):
        observable = Observable()
        retvalIsAlwaysNone = observable.do.oneWayMethodWithoutReturnValue()
        self.assertEquals(None, retvalIsAlwaysNone)
        observer = CallTrace("Observer")
        observer.something = lambda x,y: x.append(y)
        observable.addObserver(observer)
        value = []
        observable.do.something(value, 1)
        self.assertEquals([1], value)

    def testAddStrandEmptyList(self):
        observable = Observable()
        observable.addStrand((), [])
        self.assertEquals([], observable._observers)

    def testBeOne(self):
        observer = CallTrace()
        root = be((observer,))
        self.assertEquals(root, observer)

    def testBeTwo(self):
        observable = Observable()
        child0 = Observable()
        child1 = Observable()
        root = be((observable, (child0,), (child1,)))
        self.assertEquals([child0, child1], observable._observers)

    def testBeTree(self):
        observable = Observable()
        child0 = Observable(name='child0')
        child1 = Observable(name='child1')
        strand = (observable, (child0, (child1,)))
        root = be(strand)
        self.assertEquals([child0], root._observers)
        self.assertEquals([child1], child0._observers)

    def testBeToExplainTheIdeaWhithoutTestingSomethingNew(self):
        observable = Observable()
        child0 = Observable(name='child0')
        child1 = Observable(name='child1')
        child2 = Observable(name='child2')
        tree = (observable, (child0, (child1, (child2,))))
        root = be(tree)
        self.assertEquals([child0], observable._observers)
        self.assertEquals([child1], child0._observers)
        self.assertEquals([child2], child1._observers)

    def testAny(self):
        class A(Observable):
            def myThing(self):
                return self.any.myThing()
        class B(Observable):
            def myThing(self):
                yield "data"
        a = A()
        b = B()
        a.addObserver(b)
        self.assertEquals(GeneratorType, type(a.any.myThing()))
        self.assertEquals(["data"], list(a.any.myThing()))

    def testAllUnknown(self):
        class Interceptor(Observable):
            def unknown(self, message, *args, **kwargs):
                self.message = message
                self.args = args
                self.kwargs = kwargs
        interceptor = Interceptor()
        root = Observable()
        root.addObserver(interceptor)
        list(root.all.anUnknownMessage('with', unknown='arguments'))

        self.assertEquals('anUnknownMessage', interceptor.message)
        self.assertEquals(('with',), interceptor.args)
        self.assertEquals({'unknown': 'arguments'}, interceptor.kwargs)

    def testUnknownDispatchingNoImplementation(self):
        observable = Observable()
        class Listener(object):
            pass
        observable.addObserver(Listener())
        retval = observable.all.unknown('non_existing_method', 'one')
        self.assertEquals([], list(retval))

    def testUnknownDispatching(self):
        observable = Observable()
        class Listener(object):
            def method(inner, one):
                return one + " another"
        observable.addObserver(Listener())
        retval = observable.any.unknown('method', 'one')
        self.assertEquals('one another', retval)

    def testUnknownDispatchingBackToUnknown(self):
        observable = Observable()
        class Listener(object):
            def unknown(self, methodName, one):
                return ["via unknown " + one]
        observable.addObserver(Listener())
        retval = observable.any.unknown('non_existing_method', 'one')
        self.assertEquals("via unknown one", retval)

    def testSyntacticSugarIsPreserved(self):
        class WithUnknown(Observable):
            def unknown(self, methodName, *args):
                return self.all.unknown(methodName, "extra arg", *args)

        observer = CallTrace("Observer")

        withUnknown = WithUnknown()
        withUnknown.addObserver(observer)

        source = Observable()
        source.addObserver(withUnknown)
        source.do.someMethod("original arg")
        #if syntactic sugar (i.e. "do") is preseverd, it would force the call self.all.unknown directly
        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals("someMethod('extra arg', 'original arg')", str(observer.calledMethods[0]))

    def testProperErrorMessage(self):
        observable = Observable()
        try:
            answer = observable.any.gimmeAnswer('please')
            self.fail('shoud raise AttributeError')
        except AttributeError, e:
            self.assertEquals('None of the 0 observers responds to any.gimmeAnswer(...)', str(e))

    def testProperErrorMessageWhenArgsDoNotMatch(self):
        from traceback import print_exc
        observable = Observable()
        class YesObserver:
            def yes(self, oneArg): pass
        observable.addObserver(YesObserver())
        try:
            answer = observable.any.yes()
            self.fail('shoud raise AttributeError')
        except TypeError, e:
            self.assertEquals('yes() takes exactly 2 arguments (1 given)', str(e))

    def testNestedAllWithDo(self):
        self.done = False
        class A(Observable):
            def a(this):
                return this.all.a()
        class B(Observable):
            def a(this):
                return this.all.a()
        class C(Observable):
            def a(this):
                self.done = True
        a = A()
        b = B()
        c = C()
        a.addObserver(b)
        b.addObserver(c)
        result = a.do.a()
        self.assertEquals(None, result)
        self.assertTrue(self.done)

    # JJ/KvS: wij achten deze test niet nuttig. Wat wordt er hier getest?
    def xxtestNestedAllWithAny(self):
        class A(Observable):
            def a(this):
                return this.any.a()

        class B(Observable):
            def a(this):
                return this.all.a()
        class C(Observable):
            def a(this):
                return 1
        class D(Observable):
            def a(this):
                return 2
        a = A()
        b = B()
        c = C()
        d = D()
        a.addObserver(b)
        b.addObserver(c)
        b.addObserver(d)
        result = a.a()
        self.assertEquals(1, result)

    def testFixUpExceptionTraceBack(self):
        class A:
            def a(self):
                raise Exception('A.a')
            def unknown(self, msg, *args, **kwargs):
                yield self.a()
        observable = Observable()
        observable.addObserver(A())
        try:
            observable.any.a()
        except Exception:
            exType, exValue, exTraceback = sys.exc_info()
            self.assertEquals('A.a', str(exValue))
            self.assertEquals(2, len(format_tb(exTraceback)))
        try:
            list(observable.all.a())
        except Exception:
            exType, exValue, exTraceback = sys.exc_info()
            self.assertEquals('A.a', str(exValue))
            self.assertEquals(2, len(format_tb(exTraceback)))
        try:
            observable.do.a()
        except Exception:
            exType, exValue, exTraceback = sys.exc_info()
            self.assertEquals('A.a', str(exValue))
            self.assertEquals(2, len(format_tb(exTraceback)))
        try:
            observable.any.unknown('a')
        except Exception:
            exType, exValue, exTraceback = sys.exc_info()
            self.assertEquals('A.a', str(exValue))
            self.assertEquals(2, len(format_tb(exTraceback)))
        try:
            observable.any.somethingNotThereButHandledByUnknown('a')
        except Exception:
            exType, exValue, exTraceback = sys.exc_info()
            self.assertEquals('A.a', str(exValue))
            # unknown calls a(), so one extra traceback: 3
            self.assertEquals(3, len(format_tb(exTraceback)))

    def testMoreElaborateExceptionCleaning(self):
        class A(Observable):
            def a(self): return self.any.b()
        class B(Observable):
            def b(self): return self.any.c()
        class C(Observable):
            def c(self): return self.any.d()
        class D:
            def d(self): raise Exception('D.d')
        a = A()
        b = B()
        c = C()
        a.addObserver(b)
        b.addObserver(c)
        c.addObserver(D())
        try:
            a.a()
            self.fail('should raise exception')
        except:
            exType, exValue, exTraceback = sys.exc_info()
            self.assertEquals('D.d', str(exValue))
            self.assertEquals('testMoreElaborateExceptionCleaning', exTraceback.tb_frame.f_code.co_name)
            exTraceback = exTraceback.tb_next
            self.assertEquals('a', exTraceback.tb_frame.f_code.co_name)
            exTraceback = exTraceback.tb_next
            self.assertEquals('b', exTraceback.tb_frame.f_code.co_name)
            exTraceback = exTraceback.tb_next
            self.assertEquals('c', exTraceback.tb_frame.f_code.co_name)
            exTraceback = exTraceback.tb_next
            self.assertEquals('d', exTraceback.tb_frame.f_code.co_name)
            exTraceback = exTraceback.tb_next
            self.assertEquals(None, exTraceback)

    def testOneTransactionPerGenerator(self):
        txId = []
        class MyTxParticipant(Observable):
            def doSomething(self):
                txId.append(self.tx.getId())
                yield 'A'
                txId.append(self.tx.getId())
                yield 'B'
        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (MyTxParticipant(),)
                )
            )
        body = be(dna)
        scope1 = body.all.doSomething()
        scope2 = body.all.doSomething()
        scope1.next()
        scope2.next()
        scope1.next()
        scope2.next()
        self.assertTrue(txId[0] != txId[1])
        self.assertTrue(txId[1] > 0)
        self.assertTrue(txId[0] > 0)
        self.assertEquals(txId[0], txId[2])
        self.assertEquals(txId[1], txId[3])

    def testTransactionCommit(self):
        collected = {}
        class MyFirstTxParticipant(Transparant):
            def begin(self):
                self.tx.join(self)
            def doSomething(self):
                collected[self.tx.getId()] = ['first']
                yield self.any.doSomething()
            def commit(self):
                collected[self.tx.getId()].append('done 1')
        class MySecondTxParticipant(Observable):
            def begin(self):
                self.tx.join(self)
            def doSomething(self):
                collected[self.tx.getId()].append('second')
                yield 'second'
            def commit(self):
                collected[self.tx.getId()].append('done 2')
        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (MyFirstTxParticipant(),
                        (MySecondTxParticipant(),)
                    )
                )
            )
        body = be(dna)
        list(body.all.doSomething())
        self.assertEquals(['first', 'second', 'done 1', 'done 2'], collected.values()[0])

    def testAddObserversOnce(self):
        class  MyObservable(Observable):
            pass
        o1 = MyObservable(name='O1')
        o2 = MyObservable(name='O2')
        o3 = MyObservable(name='O3')
        o4 = MyObservable(name='O4')
        o5 = MyObservable(name='O5')
        helix = \
            (o1,
                (o2, )
            )
        dna =   (o3,
                    helix,
                    (o4,),
                    (o5, helix)
                 )
        root = be(dna)
        self.assertEquals([o2], o1._observers)
        self.assertEquals([], o2._observers)
        self.assertEquals([o1, o4, o5], o3._observers)
        self.assertEquals([], o4._observers)
        self.assertEquals([o1], o5._observers)

    def testResolveCallStackVariables(self):
        class StackVarHolder(Observable):
            def unknown(self, name, *args, **kwargs):
                __callstack_var_myvar__ = []
                for result in self.all.unknown(name, *args, **kwargs):
                    pass
                yield __callstack_var_myvar__

        class StackVarUser(Observable):
            def useVariable(self):
                self.myvar.append('Thingy')

        dna = \
            (Observable(),
                (StackVarHolder(),
                    (StackVarUser(),)
                )
            )
        root = be(dna)
        self.assertEquals(['Thingy'], root.any.useVariable())

    def testOnceAndOnlyOnce(self):
        class MyObserver(Observable):
            def methodOnlyCalledOnce(self, aList):
                aList.append('once')
        once = MyObserver()
        dna = \
            (Observable(),
                (once,),
                (once,)
            )
        root = be(dna)
        collector = []
        root.once.methodOnlyCalledOnce(collector)
        self.assertEquals(['once'], collector)

    def testOnceInDiamondWithTransparant(self):
        class MyObserver(Observable):
            def methodOnlyCalledOnce(self, aList):
                aList.append('once')
        once = MyObserver()
        diamond = \
            (Transparant(),
                (Transparant(),
                    (once,)
                ),
                (Transparant(),
                    (once,)
                )
            )
        root = be(diamond)
        collector = []
        root.once.methodOnlyCalledOnce(collector)
        self.assertEquals(['once'], collector)

    def testPropagateThroughAllObservablesInDiamondWithNONTransparantObservablesWithoutUnknownMethodDelegatingUnknownCalls(self):
        class MyObserver(Observable):
            def methodOnlyCalledOnce(self, aList):
                aList.append('once')
        once = MyObserver()
        diamond = \
            (Observable(),
                (Observable(),
                    (once,)
                ),
                (Observable(),
                    (once,)
                )
            )
        root = be(diamond)
        collector = []
        root.once.methodOnlyCalledOnce(collector)
        self.assertEquals(['once'], collector)

    def testNonObservableInTreeWithOnce(self):
        class MyObserver(object):
            def methodOnNonObservableSubclass(self, aList):
                aList.append('once')
        once = MyObserver()
        dna =   (Observable(),
                    (once,)
                )
        root = be(dna)
        collector = []
        root.once.methodOnNonObservableSubclass(collector)
        self.assertEquals(['once'], collector)

class TestException(Exception):
    pass

class MockObserver:

    def __init__(self):
        self.notifications = []

class ObserverA(MockObserver):

    def methodA(self, *args):
        self.notifications.append(("Method A", args))
        return "A.methodA"

class ObserverAB(MockObserver):

    def methodA(self, *args):
        self.notifications.append(("Method A", args))
        return "AB.methodA"

    def methodB(self, *args):
        self.notifications.append(("Method B", args))
        return "AB.methodB"

class DoesNotReturn(MockObserver):

    def methodA(self, *args):
        self.notifications.append(("Method A", args))
