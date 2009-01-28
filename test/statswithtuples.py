## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
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
from unittest import TestCase, main
from itertools import groupby, takewhile, dropwhile, chain

def _commonPrefix(t0, t1):
    return tuple(takewhile(lambda (l,r): l>=r, zip(t0, t1)))

def _collapse(time, t0):
    return time[:len(_commonPrefix(time, t0)) + 1]

def _groupbytime(data, t0):
    return groupby(data, lambda (time, observations): _collapse(time, t0))

def _sortbyobservation(observations):
    return sorted(observations, lambda (valuelhs,occurrencelhs), (valuerhs,occurrencerhs): cmp(valuelhs, valuerhs))

def _groupbyobservation(data):
    observations = chain(*(observations for time, observations in data))
    return groupby(_sortbyobservation(observations), lambda (value, occurrence): value)

def _countobservations(observations):
    return sum(occurrence for value, occurrence in observations)

def _merge(data):
    return tuple((value, _countobservations(observations)) for value, observations in _groupbyobservation(data))

def consolidate(data, collapseBefore=(0,0,0,0,0,0)):
    for time, data in _groupbytime(data, collapseBefore):
        yield time, _merge(data)

class GranularityException(Exception): pass

def select(data, start, until):
    def selectUntil((time, observations)):
        if len(time) < len(start) and not _commonPrefix(time, start) == ():
            raise GranularityException((time, start))
        return time < start
    return takewhile(lambda (time, observations): time < until,
                    dropwhile(selectUntil,
                        data))

class TestConsolidate(TestCase):

    def assertEqualsData(self, lhs, rhs):
        for item in lhs:
            self.assertEquals(item, rhs.next())

    def testClarifyDataStructure(self):
        t0 = (1,2,3)
        value0 = ('a','b')
        occurrence0 = 3
        observation0 = (value0, occurrence0)
        value1 = ('c','d')
        occurrence1 = 2
        observation1 = (value1, occurrence1)
        observations0 = (observation0, observation1)
        exampledata = [(t0, observations0),]
        self.assertEquals([(t0,(observation0, observation1)) ], exampledata)
        self.assertEquals([(t0,(observation0, (value1, occurrence1))) ], exampledata)
        self.assertEquals([(t0,(observation0, (value1, 2))) ], exampledata)
        self.assertEquals([(t0,((('a','b'),3), (('c','d'), 2))) ], exampledata)
        self.assertEquals([((1,2,3),((('a','b'),3),(('c','d'),2)))], exampledata)

    def testGetTooPreciseStats(self):
        data = [
            ((1,2,3),((('c','c'),1),)),
            ((2,3,4,1),((('a','b'),1),)),
            ((3,4,5,2,3),((('c','c'),1),)),
            ((4,5,6,4,5,6),((('a','b'),1),)),
        ]
        try:
            list(select(data, start=(1,2,3,4), until=(3,4,6)))
            self.fail()
        except GranularityException:
            pass

    def testGetStatistics(self):
        data = [
            ((1,2,3),((('c','c'),1),)),
            ((2,3,4,1),((('a','b'),1),)),
            ((3,4,5,2,3),((('c','c'),1),)),
            ((4,5,6,4,5,6),((('a','b'),1),)),
        ]
        p = select(data, start=(2,3,4), until=(3,4,6))
        s = consolidate(p, (999,))
        self.assertEquals([((2,), ((('a','b'),1),)), ((3,), ((('c','c'),1),),)], list(s))

    def testSelectPeriod(self):
        data = [
            ((1,2,3),(('c','c'),1)),
            ((2,3,4),(('a','b'),1)),
            ((3,4,5),(('c','c'),1)),
            ((4,5,6),(('a','b'),1)),
        ]
        p = select(data, start=(2,3,4), until=(3,4,6))
        self.assertEquals([((2, 3, 4), (('a', 'b'),1)), ((3, 4, 5), (('c', 'c'),1))], list(p))
        p = select(data, start=(2,3,5), until=(3,4,6))
        self.assertEquals([((3, 4, 5), (('c', 'c'),1))], list(p))
        p = select(data, start=(2,), until=(4,5,6))
        self.assertEquals([((2, 3, 4), (('a', 'b'),1)), ((3, 4, 5), (('c','c'),1))], list(p))
        p = select(data, start=(3,), until=(5,))
        self.assertEquals([((3, 4, 5), (('c', 'c'),1)), ((4, 5, 6), (('a','b'),1))], list(p))

    def testValuesAreSorted(self):
        c = consolidate([
            ((1,2,1),((('c','c'),1),(('a','b'),1))),
            ((1,2,2),((('a','b'),1),)),
            ((1,4,3),((('c','c'),1),)),
            ((1,4,4),((('a','b'),1),)),
        ], collapseBefore=(2,))
        self.assertEqualsData([
            ((1,), ((('a','b'),3), (('c','c'),2))),
        ], c)

    def  testWhat(self):
        c = consolidate([
            ((1,2,1),((('a','b'),1),)),
            ((2,2,2),((('a','b'),1),)),
            ((2,2,3),((('a','c'),1),)),
            ((2,3,1),((('a','c'),1),)),
            ((3,4,4),((('a','d'),1),)),
        ], collapseBefore=(2,3,0))
        self.assertEqualsData([
            ((1,), ((('a','b'),1),)),
            ((2,2), ((('a','b'),1,), (('a','c'),1),)),
            ((2,3,1), ((('a','c'),1),)),
            ((3,4,4), ((('a','d'),1),))
        ], c)

    def testConsolidateConditionallyPartially(self):
        c = consolidate([
            ((1,2,1,1),((('a','b'),1),)),
            ((1,2,1,2),((('a','b'),1),)),
            ((1,2,2,1),((('a','b'),1),)),
            ((1,2,3),((('a','c'),1),)),
            ((1,4,4),((('a','d'),1),)),
        ], collapseBefore=(1,2,3))
        self.assertEqualsData([
            ((1,2,1), ((('a','b'),2),)),
            ((1,2,2), ((('a','b'),1),)),
            ((1,2,3), ((('a','c'),1),)),
            ((1,4,4), ((('a','d'),1),))
        ], c)

    def testConsolidateConditionallyTwo(self):
        c = consolidate([
            ((1,2,1),((('a','b'),1),)),
            ((1,2,2),((('a','b'),2),)),
            ((1,4,3),((('a','c'),1),)),
            ((1,4,4),((('a','d'),2),)),
        ], collapseBefore=(1,3))
        self.assertEqualsData([
            ((1,2), ((('a','b'),3),)),
            ((1,4,3), ((('a','c'),1),)),
            ((1,4,4), ((('a','d'),2),)),
        ], c)

    def testConsolidateConditionallyOne(self):
        c = consolidate([
            ((1,2,1),((('a','b'),3),)),
            ((1,3,2),((('a','b'),2),)),
            ((1,4,3),((('a','c'),1),)),
        ], collapseBefore=(1,3,2))
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),3),)), a)
        a = c.next()
        self.assertEquals(((1,3,2), ((('a','b'),2),)), a)
        a = c.next()
        self.assertEquals(((1,4,3), ((('a','c'),1),)), a)

    def testConsolidateLowerLevel(self):
        c = consolidate([
            ((1,2,1),((('a','b'),1),)),
            ((1,2,2),((('a','b'),1),)),
            ((1,2,3),((('a','c'),1),)),
        ])
        a = c.next()
        self.assertEquals(((1,2,1), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,2,2), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,2,3), ((('a','c'),1),)), a)

    def testConsolidateHigherLevel(self):
        c = consolidate([
            ((1,2),((('a','b'),3),)),
            ((1,3),((('a','b'),2),)),
            ((2,3),((('a','b'),1),)),
        ], (9,9))
        a = c.next()
        self.assertEquals(((1,), ((('a','b'),5),)), a)
        a = c.next()
        self.assertEquals(((2,), ((('a','b'),1),)), a)

    def testConsolidateMultipleOccurencesPerPeriod(self):
        c = consolidate([
            ((1,2),((('a','b'),1),)),
            ((1,2,2,3,4,5,6),((('a','b'),1),)),
            ((1,2),((('a','c'),1),)),
            ((1,3),((('a','b'),1),)),
            ((1,3),((('a','b'),1),))
        ], (1,4))
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),2), (('a','c'),1))), a)
        a = c.next()
        self.assertEquals(((1,3), ((('a','b'),2),)), a)

    def testConsolidateMixed(self):
        c = consolidate([
            ((1,2),((('a','b'),1),)),
            ((1,2),((('a','b'),2),)),
            ((1,2),((('c','d'),3),)),
            ((1,3,4,5,6),((('a','b'),2),)),
            ((1,3),((('c','d'), 1),))
        ], (1,5))
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),3), (('c','d'),3))), a)
        a = c.next()
        self.assertEquals(((1,3), ((('a','b'),2), (('c','d'),1))), a)

    def testConsolidateDifferentTimePeriods(self):
        c = consolidate([
            ((1,2),((('a','b'),1),)),
            ((1,3),((('c','d'),2),)),
            ((1,4),((('e','f'),1),))
        ])
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),1),)), a)
        a = c.next()
        self.assertEquals(((1,3), ((('c','d'),2),)), a)
        a = c.next()
        self.assertEquals(((1,4), ((('e','f'),1),)), a)

    def testConsolidateOneTimePeriod(self):
        c = consolidate([
            ((1,2),((('a','b'),1),)),
            ((1,2),((('c','d'),1),)),
            ((1,2),((('e','f'),1),))
        ])
        a = c.next()
        self.assertEquals(((1,2), ((('a','b'),1), (('c','d'),1), (('e','f'),1))), a)

    def testToExperimentWith(self):
        from random import randint
        from time import gmtime, time
        from sys import maxint
        c = consolidate([(gmtime()[:6], (((str(randint(0,10))),1),)) for ip in xrange(10000)], (2008,1,3,8,41))
        #raw_input('before')
        print '\n'
        t0 = time()
        for stat in c:
            print stat
        t1 = time()
        print t1-t0, 's'
        #raw_input('after')

main()
