
from meresco.components import XmlCompose
from xml.sax.saxutils import escape as xmlEscape
from urllib import quote as urlQuote

RSS_TEMPLATE = """<item>
    <title>%(title)s</title>
    <description>%(description)s</description>
    <link>%(link)s</link>
    <guid>%(link)s</guid>
</item>"""

class RssItem(XmlCompose):
    def __init__(self, nsMap, title, description, linkTemplate, **linkFields):
        XmlCompose.__init__(self,
            template="ignored",
            nsMap=nsMap,
            title=title,
            description=description,
            **linkFields)
        self._linkTemplate = linkTemplate
        assertLinkTemplate(linkTemplate, linkFields)

    def createRecord(self, dataDictionary):
        try:
            link = self._linkTemplate % dict(((k, urlQuote(v)) for k,v in dataDictionary.items()))
        except KeyError:
            link = ''
        rssData = {
            'link': xmlEscape(link),
            'description': xmlEscape(dataDictionary.get('description', '')),
            'title': xmlEscape(dataDictionary.get('title', ''))
        }
        return str(RSS_TEMPLATE % rssData)

def assertLinkTemplate(linkTemplate, linkFields):
    try:
        linkTemplate % dict(((k,'value') for k in linkFields.keys()))
    except KeyError, e:
        givenArguments = len(linkFields) + len(['self', 'nsMap', 'title', 'description', 'linkTemplate'])
        raise TypeError("__init__() takes at least %s arguments (%s given, missing %s)" % (givenArguments + 1, givenArguments, str(e)))