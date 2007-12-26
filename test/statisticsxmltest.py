from cq2utils import CQ2TestCase
from meresco.components.statisticsxml import StatisticsXml

class StatisticsXmlTest(CQ2TestCase):

    def testParseDay(self):
        self.assertEquals(1167609600, StatisticsXml('ignored')._parseDay('2007-01-01'))
        self.assertEquals(1167609600 + 24 * 60 * 60 - 1, StatisticsXml('ignored')._parseDay('2007-01-01', endDay=True))

    def testParseArguments(self):
        def check(expected, query):
            statisticsxml = StatisticsXml('ignored')
            statisticsxml._query = self.shuntQuery
            statisticsxml.handleRequest(RequestURI='http://localhost/statistics?' + query)
            self.assertEquals(expected, self.query)
        check((0, 1924991999, None), '')
        check((0, 86399, ('aKey',)), 'key=aKey&beginDay=1970-01-01&endDay=1970-01-01')
        check((0, 86399, ('aKey', 'key2')), 'key=aKey&key=key2&beginDay=1970-01-01&endDay=1970-01-01')

    def shuntQuery(self, beginDay, endDay, key):
        self.query = beginDay, endDay, key