from cq2utils import CQ2TestCase
from os.path import isfile
from meresco.components.statistics import Statistics

class StatisticsTest(CQ2TestCase):

    def testStatistics(self):
        stats = Statistics(self.tempfile+'state', self.tempfile+'txlog', [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])

        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'sru'})
        self.assertEquals({
            ('date',): {
                ('2007-12-20',): 1
            },
            ('date', 'protocol'): {
                ('2007-12-20', 'sru'): 1,
            },
            ('date', 'ip', 'protocol'): {
                ('2007-12-20', '127.0.0.1', 'sru'): 1
            }
        }, stats._data)

        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'srw'})
        self.assertEquals({
            ('date',): {
                ('2007-12-20',): 2
            },
            ('date', 'protocol'): {
                ('2007-12-20', 'sru'): 1,
                ('2007-12-20', 'srw'): 1,
            },
            ('date', 'ip', 'protocol'): {
                ('2007-12-20', '127.0.0.1', 'sru'): 1,
                ('2007-12-20', '127.0.0.1', 'srw'): 1
            }
        }, stats._data)

    def testReadFile(self):
        fp = open(self.tempfile+'txlog', 'w')
        try:
            fp.write('date:2007-12-20\tip:127.0.0.1\tprotocol:sru\n')
            fp.write('date:2007-12-20\tip:127.0.0.1\tprotocol:srw\n')
        finally:
            fp.close()
        stats = Statistics(self.tempfile+'state', self.tempfile+'txlog', [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])

        self.assertEquals({
            ('date',): {
                ('2007-12-20',): 2
            },
            ('date', 'protocol'): {
                ('2007-12-20', 'sru'): 1,
                ('2007-12-20', 'srw'): 1,
            },
            ('date', 'ip', 'protocol'): {
                ('2007-12-20', '127.0.0.1', 'sru'): 1,
                ('2007-12-20', '127.0.0.1', 'srw'): 1
            }
        }, stats._data)

    def testWriteFile(self):
        def readlines():
            fp = open(self.tempfile+'txlog')
            try:
                lines = fp.readlines()
            finally:
                fp.close()
            return lines

        stats = Statistics(self.tempfile+'state', self.tempfile+'txlog', [('date',), ('date', 'protocol'), ('date', 'ip', 'protocol')])

        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'sru'})

        lines = readlines()
        self.assertEquals(1, len(lines))
        self.assertEquals('date:2007-12-20\tip:127.0.0.1\tprotocol:sru\n', lines[0])

        stats._process({'date':'2007-12-20', 'ip':'127.0.0.1', 'protocol':'srw'})
        lines = readlines()
        self.assertEquals(2, len(lines))
        self.assertEquals('date:2007-12-20\tip:127.0.0.1\tprotocol:sru\n', lines[0])
        self.assertEquals('date:2007-12-20\tip:127.0.0.1\tprotocol:srw\n', lines[1])

    def testUndefinedFieldValues(self):
        stats = Statistics(self.tempfile+'state', self.tempfile+'txlog', [('date', 'protocol')])
        stats._process({'date':'2007-12-20'})
        self.assertEquals({
            ('date', 'protocol'): {
                ('2007-12-20', '#undefined'): 1,
            },
        }, stats._data)

    def testStringToDict(self):
        stats = Statistics('file ignored', 'tx ignored', 'keys ignored')
        self.assertEquals({'a':'1', 'b':'data'}, stats._stringToDict('a:1\tb:data'))
        self.assertEquals({'a':'1', 'b':'data'}, stats._stringToDict('a:1\tb:data\t'))
        self.assertEquals({'a':'1', 'b':'d:a:t:a'}, stats._stringToDict('a:1\tb:d:a:t:a'))

    def testDictToString(self):
        stats = Statistics('file ignored', 'tx ignored', 'keys ignored')
        self.assertEquals('a:1\tb:data', stats._dictToString({'a':'1', 'b':'data'}))
        self.assertEquals('a:1\tb:data', stats._dictToString({'a':'1', 'b':'data', '':''}))


    def testEmptySnapShotState(self):
        stats = Statistics(self.tempfile+'state', self.tempfile+'txlog', [('keys',)])
        self.assertEquals({}, stats._data)

    def testSnapshotState(self):
        stats = Statistics(self.tempfile+'state', self.tempfile+'txlog', [('keys',)])
        stats._process({'keys':'2007-12-20'})
        stats._writeSnapshot()
        self.assertTrue(isfile(self.tempfile+'state'))
        stats = Statistics(self.tempfile+'state', self.tempfile+'txlog', [('keys',)])
        self.assertEquals({('keys',): {('2007-12-20',): 1}}, stats._data)