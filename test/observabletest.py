## begin license ##
#
#    "CQ2 Utils" (cq2utils) is a package with a wide range of valuable tools.
#    Copyright (C) 2005, 2006 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of "CQ2 Utils".
#
#    "CQ2 Utils" is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    "CQ2 Utils" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "CQ2 Utils"; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

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
		
	def testAll(self):
		observable = Observable()
		
		observerAB = ObserverAB()
		observerA = ObserverA()
		doesNotReturn = DoesNotReturn()

		observable.addObserver(observerAB)
		observable.addObserver(observerA)
		observable.addObserver(doesNotReturn)
		
		resultA = observable.all.methodA(0)
		resultB = observable.all.methodB(1, 2)
		self.assertEquals([
			("Method A", (0,)),
			("Method B", (1, 2))], observerAB.notifications)
		self.assertEquals([("Method A", (0,))], observerA.notifications)
		self.assertEquals([("Method A", (0,))], doesNotReturn.notifications)
		self.assertEquals("A.methodA", resultA)
		self.assertEquals("AB.methodB", resultB)
			
	def testAny(self):
		observable = Observable()
		
		doesNotReturn = DoesNotReturn()
		observerA = ObserverA()
		observerAB = ObserverAB()
		
		observable.addObserver(doesNotReturn)
		observable.addObserver(observerA)
		observable.addObserver(observerAB)
		
		resultA = observable.any.methodA(0)
		resultB = observable.any.methodB(1, 2)
		self.assertEquals([("Method A", (0,))], doesNotReturn.notifications)
		self.assertEquals([("Method A", (0,))], observerA.notifications)
		self.assertEquals([("Method B", (1, 2))], observerAB.notifications)
		
		self.assertEquals("A.methodA", resultA)
		self.assertEquals("AB.methodB", resultB)
		
		#add a test for None-result
	
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
			observable.all.mayRaiseException()
			self.fail()
		except TestException:
			pass
		self.assertEquals([], safe.notifications)
		
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
