from unittest import TestCase, main
from itertools import groupby, takewhile

def partOfTimeBefore(t0, t1):
    return tuple(takewhile(lambda (l,r): l>=r, zip(t0, t1)))

def consolidate(data, collapseBefore=(0,0,0,0,0,0)):
    for statistic, occurrences in groupby(data, lambda (t, data): t[:len(partOfTimeBefore(t, collapseBefore)) + 1]):
        yield statistic, tuple((key, len(tuple(value))) for key, value in groupby(value for key, value in occurrences))

class TestConsolidate(TestCase):

    def assertEqualsData(self, lhs, rhs):
        for item in lhs:
            self.assertEquals(item, rhs.next())

    def  testWhat(self):
        c = consolidate([
            ((1,2,1),('a','b')),
            ((2,2,2),('a','b')),
            ((2,2,3),('a','c')),
            ((2,3,1),('a','c')),
            ((3,4,4),('a','d')),
        ], collapseBefore=(2,3,0))
        self.assertEqualsData([
            ((1,), ((('a','b'),1),)),
            ((2,2), ((('a','b'),1,), (('a','c'),1),)),
            ((2,3,1), ((('a','c'),1),)),
            ((3,4,4), ((('a','d'),1),))
        ], c)

    def testConsolidateConditionallyPartially(self):
        c = consolidate([
            ((1,2,1,1),('a','b')),
            ((1,2,1,2),('a','b')),
            ((1,2,2,1),('a','b')),
            ((1,2,3),('a','c')),
            ((1,4,4),('a','d')),
        ], collapseBefore=(1,2,3))
        self.assertEqualsData([
            ((1,2,1), ((('a','b'),2),)),
            ((1,2,2), ((('a','b'),1),)),
            ((1,2,3), ((('a','c'),1),)),
            ((1,4,4), ((('a','d'),1),))
        ], c)

    def testConsolidateConditionallyTwo(self):
        c = consolidate([
            ((1,2,1),('a','b')),
            ((1,2,2),('a','b')),
            ((1,4,3),('a','c')),
            ((1,4,4),('a','d')),
        ], collapseBefore=(1,3))
        self.assertEqualsData([
            ((1,2), ((('a','b'),2),)),
            ((1,4,3), ((('a','c'),1),)),
            ((1,4,4), ((('a','d'),1),)),
        ], c)

    def testConsolidateConditionallyOne(self):
        c = consolidate([
            ((1,2,1),('a','b')),
            ((1,3,2),('a','b')),
            ((1,4,3),('a','c')),
        ], collapseBefore=(1,3,2))
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,3,2), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,4,3), ((('a','c'),1),)), a)

    def testConsolidateLowerLevel(self):
        c = consolidate([
            ((1,2,1),('a','b')),
            ((1,2,2),('a','b')),
            ((1,2,3),('a','c')),
        ])
        a = c.next()
        self.assertEquals(((1,2,1), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,2,2), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,2,3), ((('a','c'),1),)), a)

    def testConsolidateHigherLevel(self):
        c = consolidate([
            ((1,2),('a','b')),
            ((1,3),('a','b')),
            ((2,3),('a','b')),
        ], (9,9))
        a = c.next()
        self.assertEquals(((1,), ((('a','b'),2),)), a)
        a = c.next()
        self.assertEquals(((2,), ((('a','b'),1),)), a)

    def testConsolidateMultipleOccurencesPerPeriod(self):
        c = consolidate([
            ((1,2),('a','b')),
            ((1,2,2,3,4,5,6),('a','b')),
            ((1,2),('a','c')),
            ((1,3),('a','b')),
            ((1,3),('a','b'))
        ], (1,4))
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),2), (('a','c'),1))), a)
        a = c.next()
        self.assertEquals(((1,3), ((('a','b'),2),)), a)

    def testConsolidateMixed(self):
        c = consolidate([
            ((1,2),('a','b')),
            ((1,2),('c','d')),
            ((1,3,4,5,6),('a','b')),
            ((1,3),('c','d'))
        ], (1,5))
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),1), (('c','d'),1))), a)
        a = c.next()
        self.assertEquals(((1,3), ((('a','b'),1), (('c','d'),1))), a)

    def testConsolidateDifferentTimePeriods(self):
        c = consolidate([
            ((1,2),('a','b')),
            ((1,3),('c','d')),
            ((1,4),('e','f'))
        ])
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,3), ((('c','d'),1),)), a)
        a = c.next()
        self.assertEquals(((1,4), ((('e','f'),1),)), a)

    def testConsolidateOneTimePeriod(self):
        c = consolidate([
            ((1,2),('a','b')),
            ((1,2),('c','d')),
            ((1,2),('e','f'))
        ])
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),1), (('c','d'),1), (('e','f'),1))), a)

main()