## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
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

from meresco.framework.observable import Observable
from cq2utils.calltrace import CallTrace
import unittest

class ObservableTest(unittest.TestCase):

    def testAllWithoutImplementers(self):
        observable = Observable()
        responses = observable.all.someMethodNobodyIsListeningTo()
        self.assertEquals(GeneratorType, type(responses))

    def testAllWithMoreImplementers(self):
        observable = Observable()
        observerOne = CallTrace(returnValues={'aMethod': 'one'})
        observerTwo = CallTrace(returnValues={'aMethod': 'two'})
        observable.addObservers([observerOne, observerTwo])

        responses = observable.all.aMethod()

        self.assertEquals(GeneratorType, type(responses))
        self.assertEquals(['one', 'two'], list(responses))

    def testAnyCallsFirstImplementer(self):
        observable = Observable()
        observerA = ObserverA()
        observerAB = ObserverAB()
        observable.addObserver(observerA)
        observable.addObserver(observerAB)

        resultA = observable.any.methodA(0)
        resultB = observable.any.methodB(1, 2)
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

    def testAddObserversEmptyList(self):
        observable = Observable()
        observable.addObservers([])
        self.assertEquals([], observable._observers)

    def testAddObserversOne(self):
        observable = Observable()
        child = Observable()
        observable.addObservers([child])
        self.assertEquals([child], observable._observers)

    def testAddObserversTwo(self):
        observable = Observable()
        child0 = Observable()
        observable.addObservers([child0])
        child1 = Observable()
        observable.addObservers([child1])
        self.assertEquals([child0, child1], observable._observers)

    def testAddObserversTree(self):
        observable = Observable()
        child0 = Observable(name='child0')
        child1 = Observable(name='child1')
        tree = [(child0, [child1])]
        observable.addObservers(tree)
        self.assertEquals([child0], observable._observers)
        self.assertEquals([child1], child0._observers)

    def testAddOberversTreeToExplainTheIdeaWhithoutTestingSomethingNew(self):
        observable = Observable()
        child0 = Observable(name='child0')
        child1 = Observable(name='child1')
        child2 = Observable(name='child2')
        tree = [(child0, [(child1, [child2])])]
        observable.addObservers(tree)
        self.assertEquals([child0], observable._observers)
        self.assertEquals([child1], child0._observers)
        self.assertEquals([child2], child1._observers)

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
        """ON PURPOSE BROKEN CHECKIN: testSyntacticSugarIsPreserved.theory() != reality"""
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

    def testNestedAllWithAny(self):
        class A(Observable):
            def a(this):
                return this.all.a()
        class B(Observable):
            def a(this):
                return this.all.a()
        class C(Observable):
            def a(this):
                return 1
        a = A()
        b = B()
        c = C()
        a.addObserver(b)
        b.addObserver(c)
        result = a.any.a()
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
