import cPickle as pickle
from time import time
from cq2utils import CQ2TestCase
from os.path import isfile
from meresco.components.statistics import Statistics, Logger

class StatisticsTest(CQ2TestCase):

    def testStatistics(self):
        stats = Statistics(self.tempdir, [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])

        stats._clock = lambda: 0
        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'sru'})
        self.assertEquals({
                ('2007-12-20',): 1
        }, stats.get(0, 1, ('date',)))
        self.assertEquals({
                ('2007-12-20', 'sru'): 1,
        }, stats.get(0, 1, ('date', 'protocol')))
        self.assertEquals({
                ('2007-12-20', '127.0.0.1', 'sru'): 1
        }, stats.get(0, 1, ('date', 'ip', 'protocol')))

        stats._clock = lambda: 0
        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'srw'})
        self.assertEquals({
                ('2007-12-20',): 2
        }, stats.get(0, 1, ('date',)))
        self.assertEquals({
                ('2007-12-20', 'sru'): 1,
                ('2007-12-20', 'srw'): 1,
        }, stats.get(0, 1, ('date', 'protocol')))
        self.assertEquals({
                ('2007-12-20', '127.0.0.1', 'sru'): 1,
                ('2007-12-20', '127.0.0.1', 'srw'): 1
        }, stats.get(0, 1, ('date', 'ip', 'protocol')))

    def testReadTxLog(self):
        fp = open(self.tempdir + '/txlog', 'w')
        try:
            fp.write('0\tdate:2007-12-20\tip:127.0.0.1\tprotocol:sru\n')
            fp.write('0\tdate:2007-12-20\tip:127.0.0.1\tprotocol:srw\n')
        finally:
            fp.close()
        stats = Statistics(self.tempdir, [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])
        self.assertEquals({
                ('2007-12-20',): 2
        }, stats.get(0, 1, ('date',)))
        self.assertEquals({
                ('2007-12-20', 'sru'): 1,
                ('2007-12-20', 'srw'): 1,
        }, stats.get(0, 1, ('date', 'protocol')))
        self.assertEquals({
                ('2007-12-20', '127.0.0.1', 'sru'): 1,
                ('2007-12-20', '127.0.0.1', 'srw'): 1
        }, stats.get(0, 1, ('date', 'ip', 'protocol')))

    def testWriteTxLog(self):
        def readlines():
            fp = open(self.tempdir + '/txlog')
            try:
                lines = fp.readlines()
            finally:
                fp.close()
            return lines

        stats = Statistics(self.tempdir, [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])

        stats._clock = lambda: 1234
        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'sru'})

        lines = readlines()
        self.assertEquals(1, len(lines))
        self.assertEquals('1234\tdate:2007-12-20\tip:127.0.0.1\tprotocol:sru\n', lines[0])

        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'srw'})
        lines = readlines()
        self.assertEquals(2, len(lines))
        self.assertEquals('1234\tdate:2007-12-20\tip:127.0.0.1\tprotocol:sru\n', lines[0])
        self.assertEquals('1234\tdate:2007-12-20\tip:127.0.0.1\tprotocol:srw\n', lines[1])

    def testUndefinedFieldValues(self):
        stats = Statistics(self.tempdir, [('date', 'protocol')])
        stats._clock = lambda: 0
        stats._process({'date':'2007-12-20'})
        self.assertEquals({
                ('2007-12-20', '#undefined'): 1,
        }, stats.get(0, 1, ('date', 'protocol')))

    def testGetTimeOnly(self):
        stats = Statistics(self.tempdir, [('anything',)])

        stats._clock = lambda: 0
        stats._process({'anything':'value'})
        self.assertEquals({
                None: 1
        }, stats.get(0, 1))

    def testStringToDict(self):
        stats = Statistics('ignored', 'keys ignored')
        self.assertEquals({'a':'1', 'b':'data'}, stats._stringToDict('a:1\tb:data'))
        self.assertEquals({'a':'1', 'b':'data'}, stats._stringToDict('a:1\tb:data\t'))
        self.assertEquals({'a':'1', 'b':'d:a:t:a'}, stats._stringToDict('a:1\tb:d:a:t:a'))

    def testDictToString(self):
        stats = Statistics('ignored', 'keys ignored')
        self.assertEquals('a:1\tb:data', stats._dictToString({'a':'1', 'b':'data'}))
        self.assertEquals('a:1\tb:data', stats._dictToString({'a':'1', 'b':'data', '':''}))

    def testEmptySnapShotState(self):
        stats = Statistics(self.tempdir, [('keys',)])
        self.assertEquals({}, stats._data)

    def testSnapshotState(self):
        stats = Statistics(self.tempdir, [('keys',)])
        stats._clock = lambda: 0
        stats._process({'keys': '2007-12-20'})
        stats._writeSnapshot()
        self.assertTrue(isfile(self.tempdir + '/snapshot'))
        stats = Statistics(self.tempdir, [('keys',)])
        self.assertEquals({('2007-12-20',): 1}, stats.get(0, 1, ('keys',)))

    def testCrashInWriteSnapshotDuringWriteRecovery(self):
        snapshotFile = open(self.tempdir + '/snapshot', 'wb')
        theOldOne = {'0': {('keys',): {('the old one',): 3}}}
        pickle.dump(theOldOne, snapshotFile)
        snapshotFile.close()
        open(self.tempdir + '/txlog', 'w').write('0\tkeys:from_log\n')

        snapshotFile = open(self.tempdir + '/snapshot.writing', 'w')
        snapshotFile.write('boom')
        snapshotFile.close()

        stats = Statistics(self.tempdir, [('keys',)])
        self.assertEquals({('the old one',): 3, ('from_log',): 1}, stats.get(0, 1, ('keys',)))
        self.assertEquals({('the old one',): 3, ('from_log',): 1}, stats.get(0, 1, ('keys',)))
        self.assertFalse(isfile(self.tempdir + '/snapshot.writing'))

    def testCrashInWriteSnapshotAfterWriteRecovery(self):
        snapshotFile = open(self.tempdir + '/snapshot', 'wb')
        theOldOne = {('keys',): {('the old one',): 3}}
        pickle.dump(theOldOne, snapshotFile)
        snapshotFile.close()

        open(self.tempdir + '/txlog', 'w').write('keys:should_not_appear\n')

        snapshotFile = open(self.tempdir + '/snapshot.writing.done', 'w')
        theNewOne = {('keys',): {('the new one',): 3}}
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
        stats._clock = lambda: 0
        myObserver = MyObserver()
        stats.addObserver(myObserver)
        list(stats.unknown("aMessage"))
        self.assertEquals({('newValue',): 1}, stats.get(0, 1, ('message',)))

    def testCatchErrorsAndCloseTxLog(self):
        pass

    def testPeriodicSnapshot(self):
        pass

    def testAccumulateOverTime(self):
        stats = Statistics(self.tempdir, [('message',)])
        mocktime = t0 = int(time())
        stats._clock = lambda: mocktime
        stats._process({'message': 'A'})
        #count, max, min, avg, pct99
        mocktime = t1 = t0 + 1
        stats._process({'message': 'A'})
        self.assertEquals({('A',): 2}, stats.get(t0, t1, ('message',)))
