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
from sys import stdout

from os.path import join, isdir
from os import makedirs

from meresco.framework import be, Observable, TransactionScope, ResourceManager, Transparant

from meresco.components import StorageComponent, FilterField, RenameField, XmlParseLxml, XmlXPath, XmlPrintLxml, Xml2Fields, Venturi, Amara2Lxml, RewritePartname, Rss, RssItem
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
        (ResourceManager('document', lambda resourceManager: Fields2LuceneDocumentTx(resourceManager, untokenized=drilldownFieldnames)),
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
        (TransactionScope('document'),
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
                                createUploadHelix(indexHelix, storageComponent)
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
