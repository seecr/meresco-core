
from oaimain import OaiMain
from oaiidentify import OaiIdentify
from oailist import OaiList
from oaigetrecord import OaiGetRecord
from oailistmetadataformats import OaiListMetadataFormats
from oailistsets import OaiListSets
from oaisink import OaiSink
from oaijazzlucene import OaiJazzLucene
from uniquenumbergenerator import UniqueNumberGenerator

from meresco.components.lucene import LuceneIndex, unlock
from meresco.components import StorageComponent

from os.path import join

def createOaiJazz(reactor, oaiDatabasePath):
    oaiIndexPath = join(oaiDatabasePath, 'index')
    unlock(oaiIndexPath)
    oaiMetaIndexComponent = LuceneIndex(oaiIndexPath, reactor)
    oaiMetaStorageComponent = StorageComponent(join(oaiDatabasePath, 'storage'))
    numberGenerator = UniqueNumberGenerator(join(oaiDatabasePath, 'unique'))
    return OaiJazzLucene(oaiMetaIndexComponent, oaiMetaStorageComponent, numberGenerator)

def oaiOutputHelix(repositoryName, adminEmail, oaiProvenance, oaiJazz, recordStorageComponent):
    return \
        (OaiMain(),
            (OaiIdentify(repositoryName=repositoryName, adminEmail=adminEmail), ),
            (OaiList(),
                (oaiProvenance,
                    (recordStorageComponent, )
                ),
                (recordStorageComponent, ),
                (oaiJazz, ),
            ),
            (OaiGetRecord(),
                (oaiProvenance,
                    (recordStorageComponent,),
                ),
                (recordStorageComponent, ),
                (oaiJazz, )
            ),
            (OaiListMetadataFormats(),
                (oaiJazz, ),
            ),
            (OaiListSets(),
                (oaiJazz, )
            ),
            (OaiSink(), )
        )

