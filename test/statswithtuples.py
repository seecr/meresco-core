from unittest import TestCase, main
from itertools import groupby, takewhile, dropwhile

def _commonPrefix(t0, t1):
    """ returns the shortest common prefix of two tuples """
    return tuple(takewhile(lambda (l,r): l>=r, zip(t0, t1)))

def _collapse(time, t1):
    return time[:len(_commonPrefix(time, t1)) + 1]

def _groupbytime(observations, time):
    return groupby(observations, lambda (t, observation): _collapse(t, time))

def _merge(observations):
    O = sorted(observations, lambda (keylhs,valuelhs), (keyrhs,valuerhs): cmp(valuelhs, valuerhs))
    return tuple((key, len(tuple(value))) for key, value in groupby(value for key, value in O))

def consolidate(data, collapseBefore=(0,0,0,0,0,0)):
    """ turns a list of
            ((2008, 12, 31, 23, 59, 58), (v1,v2,...,vn))
            ((2008, 12, 31, 23, 59, 59), (v1,v2,...,vn))
        into a list of
            ((2008, 12, 31, 23), ((v1,v2,...vn), Cv))
        where Cv is the count of occurrences of (v1,v2,...vn),
        and (2008, 12, 31, 23) represents all longer tuples with the same common prefix
    """
    for statistic, occurrences in _groupbytime(data, collapseBefore):
        yield statistic, _merge(occurrences)

def select(data, start, until):
    return takewhile(lambda (time, observations): time < until,
                    dropwhile(lambda (time, observations): time < start,
                        data))

class TestConsolidate(TestCase):

    def assertEqualsData(self, lhs, rhs):
        for item in lhs:
            self.assertEquals(item, rhs.next())

    def testGetStatistics(self):
        data = [
            ((1,2,3),('c','c')),
            ((2,3,4),('a','b')),
            ((3,4,5),('c','c')),
            ((4,5,6),('a','b')),
        ]
        p = select(data, start=(2,3,4), until=(3,4,6))
        s = consolidate(p, (999,))
        self.assertEquals('?', list(s))

    def testSelectPeriod(self):
        data = [
            ((1,2,3),('c','c')),
            ((2,3,4),('a','b')),
            ((3,4,5),('c','c')),
            ((4,5,6),('a','b')),
        ]
        p = select(data, start=(2,3,4), until=(3,4,6))
        self.assertEquals([((2, 3, 4), ('a', 'b')), ((3, 4, 5), ('c', 'c'))], list(p))
        p = select(data, start=(2,3,5), until=(3,4,6))
        self.assertEquals([((3, 4, 5), ('c', 'c'))], list(p))
        p = select(data, start=(2,), until=(4,5,6))
        self.assertEquals([((2, 3, 4), ('a', 'b')), ((3, 4, 5), ('c','c'))], list(p))
        p = select(data, start=(3,), until=(5,))
        self.assertEquals([((3, 4, 5), ('c', 'c')), ((4, 5, 6), ('a','b'))], list(p))

    def testValuesAreSorted(self):
        c = consolidate([
            ((1,2,1),('c','c')),
            ((1,2,2),('a','b')),
            ((1,4,3),('c','c')),
            ((1,4,4),('a','b')),
        ], collapseBefore=(2,))
        self.assertEqualsData([
            ((1,), ((('a','b'),2), (('c','c'),2))),
        ], c)

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

    def XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXtestToExperimentWith(self):
        from random import randint
        from time import gmtime, time
        from sys import maxint
        c = consolidate([(gmtime()[:6], (str(randint(0,1000)),)) for ip in xrange(100000)], (2008,1,3,8,41))
        #raw_input('before')
        print '\n'
        t0 = time()
        for stat in c:
            print stat
        t1 = time()
        print t1-t0, 's'
        #raw_input('after')

main()