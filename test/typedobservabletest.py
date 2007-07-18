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

from meresco.framework.observable import Observable
from meresco.framework.typedobservable import TypedObservable, registerConverter, clearConverters, getConverter, ConvertingObservable
import unittest

class TypedObservableTest(unittest.TestCase):
	
	def setUp(self):
		clearConverters()
	
	def testAddOldObservable(self):
		class RequiresOne(TypedObservable):
			__implements__ = {}
			__requires__ = {}
			__requires__["methodOne"] = ("typeA", "typeB", "*")
		
		requires = RequiresOne()
		two = Observable()
		requires.addObserver(two)
		self.assertEquals([two], requires._observers)
		
	def testFittingLink(self):
		class RequiresOne(TypedObservable):
			__implements__ = {}
			__requires__ = {}
			__requires__["methodOne"] = ("typeA", "typeB", "*")
		
		class ImplementsOne(TypedObservable):
			__implements__ = {}
			__requires__ = {}
			__implements__["methodOne"] = ("typeA", "typeB", "*")

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
			__implements__ = {}
			__requires__ = {}
			__requires__["something"] = ("inch",)
		
		class ImplementsSomethingInCm(TypedObservable):
			__implements__ = {}
			__requires__ = {}
			__implements__["something"] = ("cm",)

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
		
