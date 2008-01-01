from cq2utils import CQ2TestCase
from meresco.components.statisticsxml import StatisticsXml
from meresco.components.statistics import Statistics

class StatisticsXmlTest(CQ2TestCase):

    def testParseDay(self):
        self.assertEquals(1167609600, StatisticsXml('ignored')._parseDay('2007-01-01'))
        self.assertEquals(1167609600 + 24 * 60 * 60 - 1, StatisticsXml('ignored')._parseDay('2007-01-01', endDay=True))

    def testParseArguments(self):
        shuntedQuery = []
        def shuntQuery(*args):
            while shuntedQuery: shuntedQuery.pop()
            shuntedQuery.append(args)
            
        def check(expected, query):
            statisticsxml = StatisticsXml('ignored')
            statisticsxml._query = shuntQuery
            statisticsxml.handleRequest(RequestURI='http://localhost/statistics?' + query)
            self.assertEquals([expected], shuntedQuery)
        check((0, 86399, ('aKey',), 0), 'key=aKey&beginDay=1970-01-01&endDay=1970-01-01')
        check((0, 86399, ('aKey', 'key2'), 12), 'key=aKey&key=key2&beginDay=1970-01-01&endDay=1970-01-01&maxResults=12')

    def testEmptyDataIntegration(self):
        stats = StatisticsXml(Statistics(self.tempdir, [('a',), ('a','b','c')]))
        result = stats.handleRequest('uri')
        self.assertEquals(stats._htmlHeader() + '<queries><query><key>a</key></query><query><key>a</key><key>b</key><key>c</key></query></queries>', ''.join(result))

    def testInvalidKey(self):
        stats = StatisticsXml(Statistics(self.tempdir, [('a',), ('a', 'b', 'c')]))
        result = stats.handleRequest(RequestURI="http://localhost/statistics?key=nonExisting")
        self.assertEquals(stats._htmlHeader() + """<error>Unknown key: ('nonExisting',)</error>""", ''.join(result))

        result = stats.handleRequest(RequestURI="http://localhost/statistics?key=a&key=b&key=d")
        self.assertEquals(stats._htmlHeader() + """<error>Unknown key: ('a', 'b', 'd')</error>""", ''.join(result))
        
    def testSortedMaxed(self):
        statisticsxml = StatisticsXml('ignored')
        result = statisticsxml._sortedMaxed([('one', 1), ('big', 100), ('not in result', 0)], 2)
        self.assertEquals([('big', 100), ('one', 1)], result)


