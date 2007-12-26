from cq2utils import CQ2TestCase
from meresco.components.statisticsxml import StatisticsXml

class StatisticsXmlTest(CQ2TestCase):

    def testParseDay(self):
        self.assertEquals(1167606000, StatisticsXml('ignored')._parseDay('2007-01-01'))
        self.assertEquals(1167606000 + 24 * 60 * 60 - 1, StatisticsXml('ignored')._parseDay('2007-01-01', endDay=True))


