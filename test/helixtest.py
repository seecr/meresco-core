from unittest import TestCase
from meresco.framework import Observable, findHelix

class HelixTest(TestCase):

    def testTupleOrObject(self):
        class MyComponent(Observable): pass
        class HisComponent(Observable): pass
        component1 = MyComponent()
        component2 = HisComponent()
        component3 = MyComponent()
        dna = [component1, (component2, [component3])]
        helix = findHelix(dna, MyComponent)
        self.assertEquals(component1, helix.next())
        self.assertEquals(component3, helix.next())

    def testSimple(self):
        class MyComponent(Observable): pass
        component1 = MyComponent()
        component2 = MyComponent()
        dna = [(component1,), (component2,)]
        helix = findHelix(dna, MyComponent)
        self.assertEquals((component1,), helix.next())
        self.assertEquals((component2,), helix.next())

    def testDifferentClasses(self):
        class MyComponent(Observable): pass
        class HisComponent(Observable): pass
        component1 = MyComponent()
        component2 = HisComponent()
        dna = [component1, component2]
        helix = findHelix(dna, MyComponent)
        self.assertEquals(component1, helix.next())
        helix = findHelix(dna, HisComponent)
        self.assertEquals(component2, helix.next())

    def testLayeredClasses(self):
        class MyComponent(Observable): pass
        class HisComponent(Observable): pass
        component1 = MyComponent()
        component2 = HisComponent()
        component3 = MyComponent()
        dna = [component1, (component2, [component3])]
        helix = findHelix(dna, MyComponent)
        self.assertEquals(component1, helix.next())
        self.assertEquals(component3, helix.next())
        helix = findHelix(dna, HisComponent)
        self.assertEquals((component2,[component3]), helix.next())
