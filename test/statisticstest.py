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
import cPickle as pickle
from time import time
from cq2utils import CQ2TestCase
from os.path import isfile
from meresco.components.statistics import Statistics, Logger, combinations, Aggregator, AggregatorException, Top100s

class StatisticsTest(CQ2TestCase):

    def testStatistics(self):
        stats = Statistics(self.tempdir, [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])

        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        stats._process({'date':['2007-12-20'], 'ip':['127.0.0.1'], 'protocol':['sru']})
        self.assertEquals({
                ('2007-12-20',): 1
        }, stats.get(('date',), ()))
        self.assertEquals({
                ('2007-12-20', 'sru'): 1,
        }, stats.get(('date', 'protocol')))
        self.assertEquals({
                ('2007-12-20', '127.0.0.1', 'sru'): 1
        }, stats.get(('date', 'ip', 'protocol')))

        stats._process({'date':['2007-12-20'], 'ip':['127.0.0.1'], 'protocol':['srw']})
        self.assertEquals({
                ('2007-12-20',): 2
        }, stats.get(('date',)))
        self.assertEquals({
                ('2007-12-20', 'sru'): 1,
                ('2007-12-20', 'srw'): 1,
        }, stats.get(('date', 'protocol')))
        self.assertEquals({
                ('2007-12-20', '127.0.0.1', 'sru'): 1,
                ('2007-12-20', '127.0.0.1', 'srw'): 1
        }, stats.get(('date', 'ip', 'protocol')))

    def testReadTxLog(self):
        fp = open(self.tempdir + '/txlog', 'w')
        try:
            fp.write("(1970, 1, 1, 0, 0, 0)\t{'date':['2007-12-20'],'ip':['127.0.0.1'],'protocol':['sru']}\n")
            fp.write("(1970, 1, 1, 0, 0, 0)\t{'date':['2007-12-20'],'ip':['127.0.0.1'],'protocol':['srw']}\n")
        finally:
            fp.close()
        stats = Statistics(self.tempdir, [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])
        self.assertEquals({
                ('2007-12-20',): 2
        }, stats.get(('date',)))
        self.assertEquals({
                ('2007-12-20', 'sru'): 1,
                ('2007-12-20', 'srw'): 1,
        }, stats.get(('date', 'protocol')))
        self.assertEquals({
                ('2007-12-20', '127.0.0.1', 'sru'): 1,
                ('2007-12-20', '127.0.0.1', 'srw'): 1
        }, stats.get(('date', 'ip', 'protocol')))

    def testWriteTxLog(self):
        def readlines():
            fp = open(self.tempdir + '/txlog')
            try:
                lines = fp.readlines()
            finally:
                fp.close()
            return lines

        stats = Statistics(self.tempdir, [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])

        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        stats._process({'date':['2007-12-20'], 'ip':['127.0.0.1'], 'protocol':['sru']})

        lines = readlines()
        self.assertEquals(1, len(lines))
        self.assertEquals("(1970, 1, 1, 0, 0, 0)\t{'date': ['2007-12-20'], 'ip': ['127.0.0.1'], 'protocol': ['sru']}\n", lines[0])

        stats._process({'date':['2007-12-20'], 'ip':['127.0.0.1'], 'protocol':['srw']})
        lines = readlines()
        self.assertEquals(2, len(lines))
        self.assertEquals("(1970, 1, 1, 0, 0, 0)\t{'date': ['2007-12-20'], 'ip': ['127.0.0.1'], 'protocol': ['sru']}\n", lines[0])
        self.assertEquals("(1970, 1, 1, 0, 0, 0)\t{'date': ['2007-12-20'], 'ip': ['127.0.0.1'], 'protocol': ['srw']}\n", lines[1])

    def testUndefinedFieldValues(self):
        stats = Statistics(self.tempdir, [('date', 'protocol')])
        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        stats._process({'date':['2007-12-20']})
        self.assertEquals({
                ('2007-12-20', '#undefined'): 1,
        }, stats.get(('date', 'protocol')))

    def testSnapshotState(self):
        stats = Statistics(self.tempdir, [('keys',)])
        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        stats._process({'keys': ['2007-12-20']})
        stats._writeSnapshot()
        self.assertTrue(isfile(self.tempdir + '/snapshot'))
        stats = Statistics(self.tempdir, [('keys',)])
        self.assertEquals({('2007-12-20',): 1}, stats.get(('keys',)))

    def testCrashInWriteSnapshotDuringWriteRecovery(self):
        stats = Statistics(self.tempdir, [('keys',)])
        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        stats._process({'keys': ['the old one']})
        stats._writeSnapshot()
        open(self.tempdir + '/txlog', 'w').write("(1970, 1, 1, 0, 0, 0)\t{'keys': ['from_log']}\n")

        snapshotFile = open(self.tempdir + '/snapshot.writing', 'w')
        snapshotFile.write('boom')
        snapshotFile.close()

        stats = Statistics(self.tempdir, [('keys',)])
        self.assertEquals({('the old one',): 1, ('from_log',): 1}, stats.get(('keys',)))

        self.assertFalse(isfile(self.tempdir + '/snapshot.writing'))

    def testCrashInWriteSnapshotAfterWriteRecovery(self):
        snapshotFile = open(self.tempdir + '/snapshot', 'wb')
        theOldOne = {'0': Top100s({('keys',): {('the old one',): 3}})}
        pickle.dump(theOldOne, snapshotFile)
        snapshotFile.close()

        open(self.tempdir + '/txlog', 'w').write('keys:should_not_appear\n')

        snapshotFile = open(self.tempdir + '/snapshot.writing.done', 'w')
        theNewOne = {'0': Top100s({('keys',): {('the new one',): 3}})}
        pickle.dump(theNewOne, snapshotFile)
        snapshotFile.close()

        stats = Statistics(self.tempdir, [('keys',)])
        self.assertEquals(theNewOne, stats._data)
        self.assertFalse(isfile(self.tempdir + '/snapshot.writing.done'))
        self.assertTrue(isfile(self.tempdir + '/snapshot'))
        self.assertEquals(theNewOne, pickle.load(open(self.tempdir + '/snapshot')))
        self.assertFalse(isfile(self.tempdir + '/txlog'))

    def testSelfLog(self):
        class MyObserver(Logger):
            def aMessage(self):
                self.log(message='newValue')
        stats = Statistics(self.tempdir, [('message',)])
        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        myObserver = MyObserver()
        stats.addObserver(myObserver)
        list(stats.unknown("aMessage"))
        self.assertEquals({('newValue',): 1}, stats.get(('message',)))

    def testSelfLogMultipleValuesForSameKey(self):
        class MyObserver(Logger):
            def aMessage(self):
                self.log(message='value1')
                self.log(message='value2')
        stats = Statistics(self.tempdir, [('message',)])
        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        myObserver = MyObserver()
        stats.addObserver(myObserver)
        list(stats.unknown("aMessage"))
        self.assertEquals({('value1',): 1, ('value2',) : 1}, stats.get(('message',)))

    def testCatchErrorsAndCloseTxLog(self):
        pass

    def testAccumulateOverTime(self):
        stats = Statistics(self.tempdir, [('message',)])
        t0 = (1970, 1, 1, 0, 0, 0)
        stats._clock = lambda: t0
        stats._process({'message': 'A'})
        #count, max, min, avg, pct99
        t1 = (1970, 1, 1, 0, 0, 1)
        stats._process({'message': 'A'})
        self.assertEquals({('A',): 2}, stats.get(('message',), (1970, 1, 1, 0, 0, 0), (1970, 1, 1, 0, 0, 2)))

    def testListKeys(self):
        stats = Statistics(self.tempdir, [('message',), ('ape', 'nut')])
        self.assertEquals([('message',), ('ape', 'nut')], stats.listKeys())

    def testEmptyDataForKey(self):
        stats = Statistics(self.tempdir, [('message',)])
        retval = stats.get(('message',))
        self.assertEquals({}, retval)

    def testObligatoryKey(self):
        stats = Statistics(self.tempdir, [('message',), ('message', 'submessage')])
        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        stats._process({'message': 'A', 'submessage': 'B'})
        retval = stats.get(('message',))
        self.assertTrue(retval)

        retval = stats.get(('message', 'submessage'))
        self.assertTrue(retval)

        try:
            stats.get(('not specified',))
            self.fail('must not accept unspecified key')
        except KeyError:
            pass

    def testFlattenValuesNothingToDo(self):
        fieldValues = ([1], [2], [5])
        fieldValuesList = combinations(fieldValues[0], fieldValues[1:])
        self.assertEquals([(1,2,5)], list(fieldValuesList))

    def testFlattenValues(self):
        fieldValues = ([1], [2,3], [4,5])
        fieldValuesList = combinations(fieldValues[0], fieldValues[1:])
        self.assertEquals([(1,2,4),(1,2,5),(1,3,4),(1,3,5)], list(fieldValuesList))

    def testFlattenValues1(self):
        fieldValues = ([1,2], [3,4,5])
        fieldValuesList = combinations(fieldValues[0], fieldValues[1:])
        self.assertEquals([(1,3), (1,4), (1,5), (2,3), (2,4), (2,5)], list(fieldValuesList))

    def testFlattenValues2(self):
        fieldValues = ([1,2], [3,4], [9])
        fieldValuesList = combinations(fieldValues[0], fieldValues[1:])
        self.assertEquals([(1,3,9),(1,4,9),(2,3,9),(2,4,9)], list(fieldValuesList))

    def testSnapshotsTiming(self):
        snapshots = []
        def shuntWriteSnapshot():
            snapshots.append('a snapshot')
            stats._lastSnapshot = stats._clock() #needed because overwritten

        stats = Statistics(self.tempdir, [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')], snapshotInterval=3600)
        stats._writeSnapshot = shuntWriteSnapshot
        stats._clock = lambda: (1970, 1, 1, 0, 0, 0)
        stats._readState() #must be done again after the clock is shunted

        stats._snapshotIfNeeded()
        self.assertEquals(0, len(snapshots))

        stats._clock = lambda: (1970, 1, 1, 0, 59, 58)
        stats._snapshotIfNeeded()
        self.assertEquals(0, len(snapshots))

        stats._clock = lambda: (1970, 1, 1, 1, 0, 0)
        stats._snapshotIfNeeded()
        self.assertEquals(1, len(snapshots))

        stats._clock = lambda: (1970, 1, 1, 1, 0, 1)
        stats._snapshotIfNeeded()
        self.assertEquals(1, len(snapshots))

    def testStatisticsAggregatorEmpty(self):
        aggregator = Aggregator(ListFactory())
        self.assertEquals([], aggregator.get((2000, 1, 1, 0, 0, 0)))

    def testStatisticsAggregatorAdd(self):
        aggregator = Aggregator(ListFactory())

        aggregator._addAt((2000, 1, 1, 0, 0, 0), "value")
        self.assertEquals(["value"], aggregator.get((2000, 1, 1, 0, 0, 0)))
        self.assertEquals(["value"], aggregator.get((2000, 1, 1, 0, 0)))
        self.assertEquals(["value"], aggregator.get((2000, 1, 1, 0)))

    def testStatisticsAggregatorAddTwiceSameTime(self):
        aggregator = Aggregator(ListFactory())
        aggregator._addAt((2000, 1, 1, 0, 0, 0), "value0")
        aggregator._addAt((2000, 1, 1, 0, 0, 0), "value1")
        self.assertEquals(["value0", "value1"], aggregator.get((2000, 1, 1, 0, 0, 0)))

    def testStatisticsAggregatorAddTwiceNewTime(self):
        aggregator = Aggregator(ListFactory())
        aggregator._addAt((2000, 1, 1, 0, 0, 0), "value0")
        aggregator._addAt((2000, 1, 1, 0, 0, 1), "value1")

        self.assertEquals(["value0"], aggregator.get((2000, 1, 1, 0, 0, 0)))
        self.assertEquals(["value1"], aggregator.get((2000, 1, 1, 0, 0, 1)))
        self.assertEquals(["value0", "value1"], aggregator.get((2000, 1, 1, 0, 0, 0), (2000, 1, 1, 0, 0, 2)))

    def testStatisticsAggregatorAggregates(self):
        aggregator = Aggregator(ListFactory())
        aggregator._addAt((2000, 1, 1, 0, 0, 0), "value00")
        aggregator._addAt((2000, 1, 1, 0, 0, 1), "value01")
        aggregator._addAt((2000, 1, 1, 0, 1, 0), "should not yet trigger")

        self.assertEquals([], aggregator._root._children[2000]._children[1]._children[1]._children[0]._children[0]._values)
        self.assertEquals(["value00"], aggregator.get((2000, 1, 1, 0, 0, 0)))

        aggregator._addAt((2000, 1, 1, 0, 2, 0), "trigger")
        self.assertEquals(["value00", "value01"], aggregator._root._children[2000]._children[1]._children[1]._children[0]._children[0]._values)
        try:
            aggregator.get((2000, 1, 1, 0, 0, 0))
            self.fail()
        except AggregatorException:
            pass
        self.assertEquals(["value00", "value01"], aggregator.get((2000, 1, 1, 0, 0)))

    def testStatisticsAggregatorAggregatesRecursivelyWithSkippedLevel(self):
        aggregator = Aggregator(ListFactory())
        aggregator._addAt((2000, 1, 1, 0, 0, 0), "value00")
        aggregator._addAt((2000, 1, 1, 0, 0, 1), "value01")
        aggregator._addAt((2000, 1, 1, 1, 0, 0), "should not yet trigger")

        aggregator._addAt((2000, 1, 1, 2, 0, 0), "trigger")
        self.assertEquals(["value00", "value01"], aggregator._root._children[2000]._children[1]._children[1]._children[0]._values)
        try:
            aggregator.get((2000, 1, 1, 0, 0))
            self.fail()
        except AggregatorException:
            pass
        self.assertEquals(["value00", "value01"], aggregator.get((2000, 1, 1, 0)))


class ListFactory(object):
    def doInit(self):
        return []
    def doAdd(self, values, value):
        values.append(value)
    def doExtend(self, values0, values1):
        values0.extend(values1)

