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

from meresco.framework.observable import Observable
from meresco.framework.typedobservable import TypedObservable, registerConverter, clearConverters, getConverter, ConvertingObservable
import unittest

class TypedObservableTest(unittest.TestCase):
	
	def setUp(self):
		clearConverters()
	
	def testAddOldObservable(self):
		class RequiresOne(TypedObservable):
			
			def __requires__(self):
				return {
					"methodOne": ("typeA", "typeB", "*")
				}
		requires = RequiresOne()
		two = Observable()
		requires.addObserver(two)
		self.assertEquals([two], requires._observers)
		
	def testFittingLink(self):
		class RequiresOne(TypedObservable):
			
			def __requires__(self):
				return {
					"methodOne": ("typeA", "typeB", "*")
				}
		class ImplementsOne(TypedObservable):
			
			def __implements__(self):
				return {
					"methodOne": ("typeA", "typeB", "*")
				}

		requires = RequiresOne()
		implements = ImplementsOne()
		requires.addObserver(implements)
		self.assertEquals([implements], requires._observers)
		
	def testRegisterConverter(self):
		converter = lambda x: x, 1
		
		registerConverter("methodOne", ("typeA"),  ("typeB", "typeC"), converter )
		self.assertEquals(converter, getConverter("methodOne", ("typeA"),  ("typeB", "typeC")))
	
	def testConvertingObservable(self):
		observations = []
		class CmObserver:
			def methodOne(self, one, two):
				observations.append((one, two))
		observer = CmObserver()
				
		cmsToInches = lambda cm1, cm2: (cm1 * 2.54, cm2 * 2.54)
		observable = ConvertingObservable("methodOne", cmsToInches)
		observable.addObserver(observer)
		observable.methodOne(1.0, 2.0)
		self.assertEquals([(2.54, 5.08)], observations)
	
	def testConversionLink(self):
		inchToCm = lambda inch: inch / 2.54
		registerConverter("something", ("inch",), ("cm",), inchToCm)
		
		class RequiresSomethingInInch(TypedObservable):
			
			def __requires__(self):
				return {
					"something": ("inch",)
				}
		class ImplementsSomethingInCm(TypedObservable):
			
			def __implements__(self):
				return {
					"something": ("cm",)
				}

		requires = RequiresSomethingInInch()
		implements = ImplementsSomethingInCm()
		requires.addObserver(implements)
		self.assertEquals(1, len(requires._observers))
		convertingObservable = requires._observers[0]
		self.assertNotEquals(implements, convertingObservable)
		self.assertEquals(ConvertingObservable, convertingObservable.__class__)
		self.assertEquals(1, len(convertingObservable._observers))
		self.assertEquals(implements, convertingObservable._observers[0])
		self.assertEquals(inchToCm, convertingObservable.something._converter)
		