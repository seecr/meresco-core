from sys import stdout

from os.path import join, isdir
from os import makedirs

from meresco.framework import be, Observable, TransactionScope, TransactionFactory, Transparant

from meresco.components import StorageComponent, FilterField, RenameField, XmlParseLxml, XmlXPath, XmlPrintLxml, Xml2Fields, TransformField, Venturi, Amara2Lxml, RewritePartname, Rss, RssItem
from meresco.components.drilldown import Drilldown, SRUDrilldownAdapter, SRUTermDrilldown, DrilldownRequestFieldnameMap
from meresco.components.http import PathFilter, ObservableHttpServer
from meresco.components.http.webrequestserver import WebRequestServer
from meresco.components.lucene import unlock, LuceneIndex, CQL2LuceneQuery, Fields2LuceneDocumentTx
from meresco.components.sru import Sru, SRURecordUpdate

from weightless import Reactor

DRILLDOWN_PREFIX = 'drilldown.'

drilldownFieldnames = [
    'drilldown.dc.subject',
]

unqualifiedTermFields = [('dc', 1.0)]

def createUploadHelix(index, storageComponent):
    fields2LuceneDocument = \
        (TransactionFactory(lambda tx: Fields2LuceneDocumentTx(tx, untokenized=drilldownFieldnames)),
            index
        )

    indexingHelix = \
        (Transparant(),
            fields2LuceneDocument,
            (FilterField(lambda name: DRILLDOWN_PREFIX + name in drilldownFieldnames),
                (RenameField(lambda name: DRILLDOWN_PREFIX + name),
                    fields2LuceneDocument
                )
            )
        )

    return \
        (Venturi(
            should=[
                ('metadata', '/document:document/document:part[@name="metadata"]/text()')
            ],
            namespaceMap={'document': 'http://meresco.com/namespace/harvester/document'}),

            (XmlXPath(['/oai:metadata/oai_dc:dc']),
                (XmlPrintLxml(),
                    (RewritePartname('dc'),
                        (storageComponent,)
                    )
                ),
                (Xml2Fields(),
                    indexingHelix,
                    (RenameField(lambda name: "dc"),
                        indexingHelix
                    ),
                ),
            ),
        )

def dna(reactor,  host, portNumber, databasePath):
    unlock(join(databasePath, 'index'))

    storageComponent = StorageComponent(join(databasePath, 'storage'))
    drilldownComponent = Drilldown(drilldownFieldnames)

    indexHelix = \
        (LuceneIndex(join(databasePath, 'index'), timer=reactor),
            (drilldownComponent,)
        )

    serverUrl = 'http://%s:%s' % (host, portNumber)

    return \
        (Observable(),
            (ObservableHttpServer(reactor, portNumber),
                (PathFilter("/sru"),
                    (Sru(host=host, port=portNumber, defaultRecordSchema='dc', defaultRecordPacking='xml'),
                        (CQL2LuceneQuery(unqualifiedTermFields),
                            indexHelix
                        ),
                        (storageComponent,),
                        (SRUDrilldownAdapter(),
                            (SRUTermDrilldown(),
                                (DrilldownRequestFieldnameMap(
                                    lambda field: DRILLDOWN_PREFIX + field,
                                    lambda field: field[len(DRILLDOWN_PREFIX):]),
                                        (drilldownComponent,)
                                )
                            )
                        )
                    )
                ),
                (PathFilter("/update"),
                    (WebRequestServer(),
                        (SRURecordUpdate(),
                            (Amara2Lxml(),
                                (TransactionScope(),
                                    createUploadHelix(indexHelix, storageComponent)
                                )
                            )
                        )
                    )
                ),
                (PathFilter('/rss'),
                    (Rss(   title = 'Meresco',
                            description = 'RSS feed for Meresco',
                            link = 'http://meresco.org',
                            maximumRecords = 15),
                        (CQL2LuceneQuery(unqualifiedTermFields),
                            indexHelix
                        ),
                        (RssItem(
                                nsMap={
                                    'dc': "http://purl.org/dc/elements/1.1/",
                                    'oai_dc': "http://www.openarchives.org/OAI/2.0/oai_dc/"
                                },
                                title = ('dc', '/oai_dc:dc/dc:title/text()'),
                                description = ('dc', '/oai_dc:dc/dc:description/text()'),
                                linkTemplate = serverUrl +   '/sru?operation=searchRetrieve&version=1.1&query=dc.identifier%%3D%(identifier)s',
                                identifier = ('dc', '/oai_dc:dc/dc:identifier/text()')),
                            (storageComponent, )
                        ),
                    )
                ),
            )
        )


config = {
    'host': 'localhost',
    'port': 8000
}

if __name__ == '__main__':
    databasePath = '/tmp/meresco'
    if not isdir(databasePath):
        makedirs(databasePath)

    reactor = Reactor()
    server = be(dna(reactor, config['host'], config['port'], databasePath))
    server.once.observer_init()

    print "Server listening on", config['host'], "at port", config['port']
    print "   - database:", databasePath, "\n"
    stdout.flush()
    reactor.loop()