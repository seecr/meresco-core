from unittest import TestCase

from merescocore.components.http import TimedDictionary

from cq2utils import CallTrace

from time import time, sleep

TWO_HOURS = 3600 * 2

class someObject(object):
    def __init__(self, initialValue):
        self.subjectToCompare = initialValue

    def __cmp__(self):
        return type(self) == type(other) \
            and cmp(self.subjectToCompare, other.subjectToCompare) \
            or cmp(type(self), type(other))

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
