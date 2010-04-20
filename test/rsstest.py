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

from cq2utils import CQ2TestCase, CallTrace
from amara.binderytools import bind_string
from urllib import urlencode

from meresco.components.rss import Rss

RSS_HEAD = """HTTP/1.0 200 OK
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
        observer = CallTrace(
            returnValues={'executeCQL': (0, [])},
            ignoredAttributes=['unknown', 'extraResponseData', 'echoedExtraRequestData'])

        rss = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
            sortKeys = 'date,,1',
            maximumRecords = '15',
        )
        rss.addObserver(observer)

        result = "".join(list(rss.handleRequest(RequestURI='/?query=aQuery')))
        self.assertEqualsWS(RSS % '', result)

    def testOneResult(self):
        observer = CallTrace(
            returnValues={
                'executeCQL': (1, [1]),
            },
            methods={
                'getRecord': lambda recordId: (g for g in ['<item><title>Test Title</title><link>Test Identifier</link><description>Test Description</description></item>']),
            },
            ignoredAttributes=['unknown', 'extraResponseData', 'echoedExtraRequestData'])

        rss = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
            sortKeys = 'date,,1',
            maximumRecords = '15',
        )
        rss.addObserver(observer)

        result = "".join(list(rss.handleRequest(RequestURI='/?query=aQuery')))
        self.assertEqualsWS(RSS % """<item>
        <title>Test Title</title>
        <link>Test Identifier</link>
        <description>Test Description</description>
        </item>""", result)

    def testError(self):
        rss = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
        )
        result = "".join(list(rss.handleRequest(RequestURI='/?query=aQuery%29'))) #%29 == ')'

        xml = bind_string(result[result.index("<?xml"):])
        self.assertEquals('ERROR Test title', str(xml.rss.channel.title))
        self.assertTrue('''An error occurred 'Unexpected token after parsing''' in str(xml.rss.channel.description), str(xml.rss.channel.description))

    def testErrorNoQuery(self):
        rss = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
        )
        result = "".join(list(rss.handleRequest(RequestURI='/')))

        xml = bind_string(result[result.index("<?xml"):])
        self.assertEquals('ERROR Test title', str(xml.rss.channel.title))
        self.assertTrue('''An error occurred 'MANDATORY parameter 'query' not supplied or empty''' in str(xml.rss.channel.description), str(xml.rss.channel.description))


    def assertMaxAndSort(self, maximumRecords, sortKey, sortDirection, rssArgs, sruArgs):
        rss = Rss(
            title = 'Test title',
            description = 'Test description',
            link = 'http://www.example.org',
            **rssArgs
        )
        recordIds = []
        def getRecord(recordId):
            recordIds.append(recordId)
            return '<item/>'

        observer = CallTrace(
            methods={
                'executeCQL': lambda start=0, stop=10, *args, **kwargs: (50, range(start, stop)),
                'getRecord': getRecord,
            },
            ignoredAttributes=['unknown', 'extraResponseData', 'echoedExtraRequestData'])
        rss.addObserver(observer)

        result = "".join(list(rss.handleRequest(RequestURI='/?query=aQuery&' + urlencode(sruArgs))))

        method = observer.calledMethods[0]
        self.assertEquals('executeCQL', method.name)
        self.assertEquals(sortKey, method.kwargs['sortBy'])
        self.assertEquals(sortDirection, method.kwargs['sortDescending'])
        self.assertEquals(maximumRecords, len(recordIds))

    def testMaxAndSort(self):
        self.assertMaxAndSort(10, None, None, rssArgs={}, sruArgs={})
        self.assertMaxAndSort(15, None, None, rssArgs={'maximumRecords':'15'}, sruArgs={})
        self.assertMaxAndSort(20, None, None, rssArgs={'maximumRecords':'15'}, sruArgs={'maximumRecords':'20'})
        self.assertMaxAndSort(20, None, None, rssArgs={}, sruArgs={'maximumRecords':'20'})

        self.assertMaxAndSort(10, 'sortable', True, rssArgs={'sortKeys':'sortable,,1'}, sruArgs={})
        self.assertMaxAndSort(10, 'othersortable', False, rssArgs={'sortKeys':'sortable,,1'}, sruArgs={'sortKeys':'othersortable,,0'})
        self.assertMaxAndSort(10, 'othersortable', False, rssArgs={}, sruArgs={'sortKeys':'othersortable,,0'})

    def testContentType(self):
        observer = CallTrace(
            returnValues={'executeCQL': (0, [])},
            ignoredAttributes=['unknown', 'extraResponseData', 'echoedExtraRequestData'])
        rss = Rss(title = 'Title', description = 'Description', link = 'Link')
        rss.addObserver(observer)

        result = "".join(rss.handleRequest())
        self.assertTrue('Content-Type: application/rss+xml' in result, result)


