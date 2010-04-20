## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
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
from unittest import TestCase

from meresco.components import TimedDictionary

from cq2utils import CallTrace

from time import time, sleep

TWO_HOURS = 3600 * 2
ONE_HOUR = 3600

class SomeObject(object):
    def __init__(self, id):
        self.id = id

    def _raise(self):
        raise Exception("Should not happen in this testsituation")

class TimedDictionaryTest(TestCase):
    def testBasicGetAndPut(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict['key'] = 'value'
        self.assertEquals('value', timedDict['key'])

        timedDict['key'] = 'otherValue'
        self.assertEquals('otherValue', timedDict['key'])
        timedDict['key'] = 5
        self.assertEquals(5, timedDict['key'])
        timedDict['key'] = 5.0
        self.assertEquals(5.0, timedDict['key'])
        timedDict['key'] = ['someMutable', 5]
        self.assertEquals(['someMutable', 5], timedDict['key'])

        self.assertEquals(['someMutable', 5], timedDict.get('key'))

        self.assertRaises(TypeError, timedDict.__setitem__, [], 'value')
        self.assertRaises(KeyError, timedDict.__getitem__, 'iamnothere')
        self.assertEquals(None, timedDict.get('iamnothere'))
        self.assertEquals('MARK', timedDict.get('iamnothere', 'MARK'))

    def testBasicContains(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict[5] = 'five'
        timedDict['six'] = 6
        self.assertTrue(5 in timedDict)
        self.assertTrue('six' in timedDict)
        self.assertFalse(42 in timedDict)
        self.assertFalse(None in timedDict)

        self.assertTrue(timedDict.has_key(5))
        self.assertTrue(timedDict.has_key('six'))
        self.assertFalse(timedDict.has_key(42))
        self.assertFalse(timedDict.has_key(None))

    def testBasicDeletion(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict['key'] = 'five'

        try:
            del timedDict['key']
        except:
            self.fail("This shouldn't happen.")
        self.assertRaises(KeyError, timedDict.__delitem__, 'idontexist')

    def testOrderIsKeptInternally(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict[3] = SomeObject(1)
        timedDict[1] = SomeObject(10)
        timedDict[2] = SomeObject(20)

        self.assertEquals([3, 1, 2], timedDict._list)

        timedDict[1] = SomeObject(23)
        self.assertEquals([3, 2, 1], timedDict._list)

        timedDict[0] = SomeObject(23.01)
        self.assertEquals([3, 2, 1, 0], timedDict._list)

        del timedDict[2]
        self.assertEquals([3, 1, 0], timedDict._list)

    def testGetTime(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict[1] = SomeObject('id1')
        self.assertTrue(time() - timedDict.getTime(1) < 2.0)

    def testTouch(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict[1] = SomeObject('id1')
        timedDict[2] = SomeObject('id2')

        self.assertEquals([1, 2], timedDict._list)
        timedDict.touch(1)
        self.assertEquals([2, 1], timedDict._list)

    def testPurge(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict[1] = SomeObject('id1')
        timedDict[2] = SomeObject('id2')
        timedDict._now = lambda : time() + ONE_HOUR
        self.assertEquals([1, 2], timedDict._list)

        timedDict[3] = SomeObject('id3')
        timedDict.touch(2)
        timedDict._now = lambda : time() + TWO_HOURS
        timedDict.purge()
        self.assertEquals([3, 2], timedDict._list)
        timedDict._now = lambda : time() + TWO_HOURS + TWO_HOURS
        timedDict.purge()
        self.assertEquals([], timedDict._list)

    def testPurgeOnSetItem(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict[1] = SomeObject('id1')
        timedDict._now = lambda : time() + TWO_HOURS
        timedDict[2] = SomeObject('id2')

        self.assertEquals([2], timedDict._list)

    def testDeleteExpiredOnGetItem(self):
        timedDict = TimedDictionary(TWO_HOURS)
        timedDict[1] = SomeObject('id1')
        timedDict._now = lambda : time() + TWO_HOURS

        self.assertRaises(KeyError, timedDict.__getitem__, 1)
        self.assertEquals([], timedDict._list)

    def testExpiredOnInShouldReturnDefaultOnGetWithoutAnException(self):
        timedDict = TimedDictionary(TWO_HOURS)
        setTime = time()
        timedDict._now = lambda : setTime
        timedDict[1] = SomeObject('id1')

        timedDict._now = lambda : setTime + TWO_HOURS
        try:
            1 in timedDict
        except KeyError:
            self.fail("Key shouldn't have expired yet.")
        except:
            self.fail("This should not happen.")

        timedDict._now = lambda : setTime + TWO_HOURS + 0.000001

        self.assertEquals(None, timedDict.get(1))
        self.assertEquals('a default', timedDict.get(1, 'a default'))
        self.assertEquals([], timedDict._list)
