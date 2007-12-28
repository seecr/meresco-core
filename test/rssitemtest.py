from cq2utils import CQ2TestCase as TestCase

from meresco.components.rssitem import RssItem
from StringIO import StringIO

class RssItemTest(TestCase):
    def testOne(self):
        item = RssItem(
            nsMap = {},
            title = ('part1', '/dc/title/text()'),
            description = ('part1', '/dc/description/text()'),
            linkTemplate='http://example.org/show?recordId=%(recordId)s&type=%(type)s',
            recordId = ('part2', '/meta/upload/id/text()'),
            type = ('part2', '/meta/type/text()')
        )
        item.addObserver(MockStorage())
        result = "".join(list(item.getRecord('aap')))
        self.assertEqualsWS("""<item>
    <title>Title</title>
    <description>Description</description>
    <link>http://example.org/show?recordId=12%2834%29&amp;type=Type</link>
</item>""", result)

    def testNoDescription(self):
        item = RssItem(
            nsMap = {},
            title = ('part1', '/dc/title/text()'),
            description = ('partNoDescription', '/dc/description/text()'),
            linkTemplate = 'http://www.example.org/'
        )
        item.addObserver(MockStorage())
        result = "".join(list(item.getRecord('aap')))
        self.assertEqualsWS("""<item>
    <title>Title</title>
    <description></description>
    <link>http://www.example.org/</link>
</item>""", result)

    def testPartOfLinkTemplateNotFound(self):
        item = RssItem(
            nsMap = {},
            title = ('part1', '/dc/title/text()'),
            description = ('partNoDescription', '/dc/description/text()'),
            linkTemplate = 'http://www.example.org/%(something)s',
            something = ('part1', '/dc/not/existing/text()'),
        )
        item.addObserver(MockStorage())
        result = "".join(list(item.getRecord('aap')))
        self.assertEqualsWS("""<item>
    <title>Title</title>
    <description></description>
    <link></link>
</item>""", result)
        
    def testPartOfLinkTemplateNotConfigured(self):
        try:
            item = RssItem(
                nsMap = {},
                title = ('part1', '/dc/title/text()'),
                description = ('partNoDescription', '/dc/description/text()'),
                linkTemplate = 'http://www.example.org/%(notMentioned)s',
            )
            self.fail()
        except TypeError, e:
            self.assertEquals("__init__() takes at least 6 arguments (5 given, missing 'notMentioned')", str(e))


class MockStorage(object):
    def getStream(self, id, partname):
        if partname == 'part1':
            return StringIO('<dc><title>Title</title><description>Description</description></dc>')
        elif partname == 'part2':
            return StringIO('<meta><upload><id>12(34)</id></upload><type>Type</type></meta>')
        if partname == 'partNoDescription':
            return StringIO('<dc><title>Title</title></dc>')

            