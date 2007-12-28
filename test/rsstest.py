## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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

from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace

from meresco.components.rss import Rss

from sru.srutest import MockListeners, MockHits


RSS_HEAD = """HTTP/1.0 200 Ok
Content-Type: application/rss+xml

<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
%s
</channel>
</rss>"""

RSS = RSS_HEAD % """<title>Test title</title>
<description>Test description</description>
<link>http://www.example.org</link>
%s
"""

class RssTest(CQ2TestCase):

    def testNoResults(self):
        observer = MockListeners(MockHits(0))

        rss = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
            recordSchema = 'dc',
            sortKeys = 'date,,1',
            maximumRecords = '15',
            x_recordSchema = ['one', 'two']
        )
        rss.addObserver(observer)

        result = "".join(list(rss.handleRequest()))
        self.assertEqualsWS(RSS % '', result)

    def testOneResult(self):
        def yieldRecord(recordId):
            yield '<title>Test Title</title><link>Test Identifier</link><description>Test Description</description>'

        listeners = MockListeners(MockHits(1))
        listeners.yieldRecord = yieldRecord

        rss = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
            recordSchema = 'dc',
            sortKeys = 'date,,1',
            maximumRecords = '15',
            x_recordSchema = ['one', 'two']
        )
        rss.addObserver(listeners)

        result = "".join(list(rss.handleRequest()))
        self.assertEqualsWS(RSS % """<item>
        <title>Test Title</title>
        <link>Test Identifier</link>
        <description>Test Description</description>
        </item>""", result)

    def xxxtestWriteResultWithXmlEscaping(self):
        def yieldRecord(recordId, recordSchema):
            yield '<document><xmlfields><dctitle>&amp;&lt;&gt;</dctitle></xmlfields></document>'

        listeners = MockListeners(MockHits(1))
        listeners.yieldRecord = yieldRecord

        component = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
            recordSchema = 'dc',
            sortKeys = 'date,,1',
            maximumRecords = '15',
            x_recordSchema = ['one', 'two']
        )
        component.addObserver(listeners)

        result = "".join(list(component.handleRequest()))
        self.assertEqualsWS(RSS % """<item>
        <title>&amp;&lt;&gt;</title>
        <link></link>
        <description></description>
        </item>""", result)

    def xxxtestError(self):
        result = "".join(list(Rss(self.profiles).handleRequest(RequestURI='/?query=aQuery%29'))) #%29 == ')'

        ERROR= RSS_HEAD % """
<title>ERROR Test title</title><link>http://www.example.org</link><description>An error occurred 'Unexpected token after parsing, check parser for greediness ([)], cqlparser.cqlparser.CQL_QUERY(cqlparser.cqlparser.SCOPED_CLAUSE(cqlparser.cqlparser.SEARCH_CLAUSE(cqlparser.cqlparser.SEARCH_TERM('aQuery'))))).'</description>"""
        self.assertEqualsWS(ERROR, result)

    def xxxtestMaximumRecordsAndSortKeys(self):
        rss = Rss(self.profiles)

        profile = self.profiles['default']
        newArguments, recordSchema = rss._parseArguments(profile, {})

        self.assertEquals(['15'], newArguments['maximumRecords'])
        self.assertEquals(['sortField,,1'], newArguments['sortKeys'])

        profile = self.profiles['default']
        newArguments, recordSchema = rss._parseArguments(profile, { 'maximumRecords': ['42'], 'sortKeys': ['SORTKEY'] })

        self.assertEquals(['42'], newArguments['maximumRecords'])
        self.assertEquals(['SORTKEY'], newArguments['sortKeys'])

    def xxxtestNoSortKeysInProfile(self):
        rss = Rss(self.profiles)
        profile = self.profiles['default']
        profile.sortKeys = lambda: None

        newArguments, recordSchema = rss._parseArguments(profile, {})

        self.assertFalse(newArguments.has_key('sortKeys'))

    def xxxtestSelectOtherProfile(self):
        class OtherProfile(RssProfile):
            def __init__(self):
                self._item = lambda document: [
                    ('title', document.xmlfields.dctitle),
                    ('link', document.xmlfields.identifier),
                    ('description', document.xmlfields.dcdescription)
                ]
                self._rss = Setters()
                self._channel = Setters()
                self._rss.maximumRecords = 15
                self._rss.sortKeys = 'generic4,,1'
                self._rss.recordSchema = 'document'
                self._channel.title = 'Test title'
                self._channel.link = 'http://www.example.org'
                self._channel.description = 'Test description'

        profile = OtherProfile()
        profile._channel.extraTitle = 'Other'
        profile._item = lambda x: [('title', 'othertitle')]

        component = Rss(self.profiles)
        component.addObserver(MockListeners(MockHits(0)))
        component._profiles['otherprofile'] = profile

        result = "".join(list(component.handleRequest(RequestURI='/?query=aQuery&x-rss-profile=otherprofile')))

        self.assertTrue("""<extraTitle>Other</extraTitle>""" in result)

    def testContentType(self):
        listeners = MockListeners(MockHits(0))
        rss = Rss(title = 'Title', description = 'Description', link = 'Link')
        rss.addObserver(listeners)

        result = "".join(list(rss.handleRequest()))
        self.assertTrue('Content-Type: application/rss+xml' in result, result)

    def xxxtestProfileDefaultsToDefault(self):
        component = Rss(self.profiles)
        profile = component._getProfile({'x-rss-profile': ['nonExistingProfile']})
        self.assertEquals(self.profiles['default'], profile)


