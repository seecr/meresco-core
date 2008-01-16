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
from cq2utils import CQ2TestCase
from meresco.components.statisticsxml import StatisticsXml
from meresco.components.statistics import Statistics

class StatisticsXmlTest(CQ2TestCase):

    def testParseTime(self):
        s = StatisticsXml('ignored')
        self.assertEquals((2007,), s._parseTime('2007'))
        self.assertEquals((2007, 1), s._parseTime('2007-01'))
        self.assertEquals((2007, 1, 1), s._parseTime('2007-01-01'))
        self.assertEquals((2007, 1, 1, 0), s._parseTime('2007-01-01T00'))
        self.assertEquals((2007, 1, 1, 0, 0), s._parseTime('2007-01-01T00:00'))
        self.assertEquals((2007, 1, 1, 0 , 0, 0), s._parseTime('2007-01-01T00:00:00Z'))

    def testParseNonsense(self):
        s = StatisticsXml('ignored')
        s._listKeys = lambda: []

        xx = s.handleRequest(RequestURI='http://localhost/statistics?fromTime=garbage')
        result = "".join(list(s.handleRequest(RequestURI='http://localhost/statistics?fromTime=garbage')))
        self.assertTrue("<error>Invalid Time Format" in result, result)
        result = "".join(list(s.handleRequest(RequestURI='http://localhost/statistics?maxResults=garbage')))
        self.assertTrue("<error>maxResults must be number" in result, result)

    def testParseArguments(self):
        shuntedQuery = []
        def shuntQuery(*args):
            while shuntedQuery: shuntedQuery.pop()
            shuntedQuery.append(args)
            return ""

        def check(expected, query):
            statisticsxml = StatisticsXml('ignored')
            statisticsxml._listKeys = lambda: []
            statisticsxml._query = shuntQuery
            list(statisticsxml.handleRequest(RequestURI='http://localhost/statistics?' + query))
            self.assertEquals([expected], shuntedQuery)
        check(((1970, 1, 1), (1970, 1, 2), ('aKey',), 0), 'key=aKey&fromTime=1970-01-01&toTime=1970-01-02')
        check(((1970, 1, 1), (1970, 1, 2), ('aKey', 'key2'), 12), 'key=aKey&key=key2&fromTime=1970-01-01&toTime=1970-01-02&maxResults=12')

    def testNoKeysGivenReturnsKeys(self):
        stats = StatisticsXml(Statistics(self.tempdir, [('a',), ('a','b','c')]))
        result = "".join(list(stats.handleRequest('uri')))
        self.assertTrue("""<availableKeys><key><keyElement>a</keyElement></key><key><keyElement>a</keyElement><keyElement>b</keyElement><keyElement>c</keyElement></key></availableKeys></statistics>""" in result, result)

    def testInvalidKey(self):
        stats = StatisticsXml(Statistics(self.tempdir, [('a',), ('a', 'b', 'c')]))
        result = stats.handleRequest(RequestURI="http://localhost/statistics?key=nonExisting")
        self.assertTrue("""<error>Unknown key: ('nonExisting',)</error>""" in ''.join(result))

        result = stats.handleRequest(RequestURI="http://localhost/statistics?key=a&key=b&key=d")
        self.assertTrue("""<error>Unknown key: ('a', 'b', 'd')</error>""" in ''.join(result))

    def testSorted(self):
        statisticsxml = StatisticsXml('ignored')
        result = statisticsxml._sorted([('one', 1), ('big', 100)])
        self.assertEquals([('big', 100), ('one', 1)], result)

    def testResponseFormat(self):
        statisticsxml = StatisticsXml(Statistics(self.tempdir, [('a',), ('a', 'b', 'c')]))
        result = ''.join(list(statisticsxml.handleRequest(RequestURI="http://localhost/statistics?key=a&fromTime=2008&toTime=2008-01-01")))
        self.assertTrue("""HTTP/1.0 200 OK""" in result, result)
        self.assertTrue("""<?xml""" in result, result)
        self.assertTrue("""<statistics""" in result, result)
        self.assertTrue("""<serverTime""" in result, result)
        self.assertTrue("""<fromTime>2008""" in result, result)
        self.assertTrue("""<toTime>2008-01-01""" in result, result)
        self.assertTrue("""<serverTime""" in result, result)



