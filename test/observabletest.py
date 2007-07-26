## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
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
from types import GeneratorType

from meresco.framework.observable import Observable, Function, FunctionObservable
from cq2utils.calltrace import CallTrace
import unittest

class ObservableTest(unittest.TestCase):

    def testNotifications(self):
        observable = Observable()
        one = MockObserver()
        two = MockObserver()
        observable.addObserver(one)
        observable.addObserver(two)
        observable.changed("A")
        observable.changed("B", "C")
        self.assertEquals([("A",), ("B", "C")], one.notifications)
        self.assertEquals([("A",), ("B", "C")], two.notifications)

    def testProcess(self):
        observable = Observable()
        observerOne = CallTrace('ObserverOne')
        observerOne.returnValues['notify'] = True
        observerTwo = CallTrace('ObserverTwo')
        observerTwo.returnValues['notify'] = 1
        observerThree = CallTrace('ObserverThree')
        observerThree.returnValues['notify'] = 'yes'

        observable.addObserver(observerOne)
        observable.addObserver(observerTwo)
        observable.addObserver(observerThree)

        result = observable.process('This is a cool test')

        self.assertEquals(True, result)
        self.assertEquals(1, len(observerOne.calledMethods))
        self.assertEquals(0, len(observerTwo.calledMethods))
        self.assertEquals(0, len(observerThree.calledMethods))

    def testProcessNoneReturnValues(self):
        observable = Observable()
        observerOne = CallTrace('Observer')
        observerOne.returnValues['notify'] = None
        observerTwo = CallTrace('ObserverTwo')
        observerTwo.returnValues['notify'] = ''

        observable.addObserver(observerOne)
        observable.addObserver(observerTwo)

        result = observable.process('This is a cool test')

        self.assertEquals('', result)

    def testFunctionWrapperOneResultValue(self):
        class MockExtendedObservable(Observable):
            def notify(self, arg0, arg1):
                self.changed("The Result " + arg0)
        f = Function(MockExtendedObservable())
        self.assertEquals("The Result A", f("A", "B"))

    def testFunctionWrapperNoResultValue(self):
        class MockExtendedObservable(Observable):
            def notify(self, arg0, arg1):
                self.changed()
        f = Function(MockExtendedObservable())
        self.assertEquals(None, f("A", "B"))

    def testFunctionWrapperNResultValues(self):
        class MockExtendedObservable(Observable):
            def notify(self, arg0, arg1):
                self.changed("Extended " + arg0, "Extended " + arg1, "Additional Argument")
        f = Function(MockExtendedObservable())
        self.assertEquals(("Extended A", "Extended B", "Additional Argument"), f("A", "B"))

    def testFunctionObservable(self):
        function = lambda x: x

        observable = FunctionObservable(function)
        observer = MockObserver()
        observable.addObserver(observer)

        observable.notify("A")
        self.assertEquals([("A",)], observer.notifications)

    def testFunctionObservableTupleResult(self):
        function = lambda arg0: ("Extended " + arg0, "Additional Argument")

        observable = FunctionObservable(function)
        one = MockObserver()
        observable.addObserver(one)

        observable.notify("A")
        self.assertEquals([("Extended A", "Additional Argument")], one.notifications)

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
            self.assertEquals('None of the 0 delegates answers any.gimmeAnswer(...)', str(e))

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
            
     

class TestException(Exception):
    pass

class MockObserver:

    def __init__(self):
        self.notifications = []

    def notify(self, *args):
        self.notifications.append(args)

    def notifyRaisesException(self, *args):
        self.notifications.append(args)
        raise TestException("notifyRaisesException")

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
