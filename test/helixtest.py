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
from unittest import TestCase
from meresco.framework import Observable, findHelix, link, be

class HelixTest(TestCase):

    def testTupleOrObject(self):
        class MyComponent(Observable): pass
        class HisComponent(Observable): pass
        component1 = MyComponent()
        component2 = HisComponent()
        component3 = MyComponent()
        dna = (component1, (component2, (component3,)))
        helix = findHelix(dna, MyComponent)
        self.assertEquals((component1,(component2, (component3,))), helix.next())
        self.assertEquals((component3,), helix.next())

    def testSimple(self):
        class MyComponent(Observable): pass
        component1 = MyComponent()
        component2 = MyComponent()
        dna = (component1, (component2,))
        helix = findHelix(dna, MyComponent)
        self.assertEquals((component1, (component2,)), helix.next())
        self.assertEquals((component2,), helix.next())

    def testDifferentClasses(self):
        class MyComponent(Observable): pass
        class HisComponent(Observable): pass
        component1 = MyComponent()
        component2 = HisComponent()
        dna = (component1, (component2,))
        helix = findHelix(dna, MyComponent)
        self.assertEquals((component1, (component2,)), helix.next())
        helix = findHelix(dna, HisComponent)
        self.assertEquals((component2,), helix.next())

    def testLayeredClasses(self):
        class MyComponent(Observable): pass
        class HisComponent(Observable): pass
        component1 = MyComponent()
        component2 = HisComponent()
        component3 = MyComponent()
        dna = (component1, (component2, (component3,)))
        helix = findHelix(dna, MyComponent)
        self.assertEquals((component1, (component2, (component3,))), helix.next())
        self.assertEquals((component3,), helix.next())
        helix = findHelix(dna, HisComponent)
        self.assertEquals((component2, (component3,)), helix.next())

    #def testLink(self):
        #class MyComponent(Observable): pass
        #class HisComponent(Observable): pass
        #component1 = MyComponent()
        #component2 = HisComponent()
        #component3 = MyComponent()
        #dna = (component1, (component2, (component3,)), link(component2))
        #lifeForm = be(dna)
        #self.assertEquals((component1, (component2, (component3,)), component2), lifeForm)
