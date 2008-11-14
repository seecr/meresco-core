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

from meresco.framework import be, Observable, TransactionScope, ResourceManager

from meresco.components import StorageComponent, XmlPrintLxml, Xml2Fields, Amara2Lxml
from meresco.components.http import PathFilter, ObservableHttpServer
from meresco.components.http.webrequestserver import WebRequestServer
from meresco.components.lucene import unlock, LuceneIndex, CQL2LuceneQuery, Fields2LuceneDocumentTx
from meresco.components.sru import Sru, SRURecordUpdate

from weightless import Reactor

class SetIdentifier(Observable):
    def add(self, identifier, partname, data):
        self.tx.locals['id'] = identifier
        yield self.all.add(identifier, partname, data)

def dna(reactor,  host, portNumber, databasePath):
    unlock(join(databasePath, 'index'))

    storageComponent = StorageComponent(join(databasePath, 'storage'))
    indexHelix = (LuceneIndex(join(databasePath, 'index'), timer=reactor), )

    return \
        (Observable(),
            # The HTTP server which handles both the queries as the updates
            (ObservableHttpServer(reactor, portNumber),
                # Filter out all requests that start with /sru
                (PathFilter("/sru"),
                    # Create the SRU component that will respond to queries
                    (Sru(host=host, port=portNumber),
                        # Convert the given CQL into the Lucene query language
                        (CQL2LuceneQuery([]),
                            # Use the index to query Lucene and return the
                            # identifiers of the matching documents.
                            indexHelix
                        ),
                        # Retrieve the documents with the given identifiers and
                        # send them back as the response.
                        (storageComponent,),
                    )
                ),

                # Filter out all requests that start with /update
                (PathFilter("/update"),
                    # Translate the HTTP request into the format the
                    # SRURecordUpdate component understands.
                    (WebRequestServer(),
                        # Create the SRURecordUpdate which understands the
                        # SRUUpdate layer.
                        (SRURecordUpdate(),
                            # Convert the Amara based xml object from the
                            # SRUupdate component into an Lxml based xml object
                            # for futher processing.
                            (Amara2Lxml(),
                                # Convert the Lxml based xml object into plain
                                # text
                                (XmlPrintLxml(),
                                    # Store the data in the storage
                                    (storageComponent,)
                                ),
                                # Start a new transaction in which the given xml
                                # will be indexed.
                                (TransactionScope('record'),
                                    # Every transaction needs an identifier. The
                                    # identifier provided by the SRURecordUpdate
                                    # will be set into the transaction.
                                    (SetIdentifier(),
                                        # The given xml will be transformed into
                                        # Fields. by traversing the xml
                                        # from root to all leaves. Each pair
                                        # will then be added to the index.
                                        (Xml2Fields(),
                                            # Add all created fields to an
                                            # collection of fields. Once all
                                            # fields have been created, commit
                                            # the transaction.
                                            (ResourceManager('record', lambda resourceManager: Fields2LuceneDocumentTx(resourceManager, untokenized=[])),
                                                # Commit the created fields
                                                # into the index.
                                                indexHelix
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )


if __name__ == '__main__':
    databasePath = '/tmp/meresco'
    host = 'localhost'
    port = 8000

    if not isdir(databasePath):
        makedirs(databasePath)

    reactor = Reactor()
    server = be(dna(reactor, host, port, databasePath))
    server.once.observer_init()

    print "Server listening on", host, "at port", port
    print "   - database:", databasePath, "\n"
    stdout.flush()
    reactor.loop()
