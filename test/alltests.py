#!/usr/bin/env python2.5

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

import os, sys
os.system('find .. -name "*.pyc" | xargs rm -f')

from glob import glob
for path in glob('../deps.d/*'):
    sys.path.insert(0, path)

sys.path.insert(0, "..")

import unittest

from accumulatetest import AccumulateTest
from contextsettest import ContextSetTest
from cqlparsetreetolucenequerytest import CqlParseTreeToLuceneQueryTest
from cql2lucenequerytest import Cql2LuceneQueryTest
from documenttest import DocumentTest
from drilldownfilterstest import DrilldownFiltersTest
from drilldowntest import DrilldownTest
from fields2lucenedocumenttest import Fields2LuceneDocumentTest
from generatorutilstest import GeneratorUtilsTest
from hitstest import HitsTest
from logcomponenttest import LogComponentTest
from logobservertest import LogObserverTest
from lucenerawdocsetstest import LuceneRawDocSetsTest
from lucenetest import LuceneTest
from observabletest import ObservableTest
from observablehttpservertest import ObservableHttpServerTest
from storagecomponenttest import StorageComponentTest
from storageharvestertest import StorageHarvesterTest
from rsstest import RssTest
from rssitemtest import RssItemTest
from statisticstest import StatisticsTest
from statisticsxmltest import StatisticsXmlTest
from venturitest import VenturiTest
from xmlpumptest import XmlPumpTest
from xml2fieldstest import Xml2FieldsTest
from xpath2fieldtest import XPath2FieldTest
from xpathtransform2fieldtest import XPathTransform2FieldTest
from xslicetest import XSliceTest

from http.basicauthenticationtest import BasicAuthenticationTest
from http.fileservertest import FileServerTest
from http.pathfiltertest import PathFilterTest
from http.sessionhandlertest import SessionHandlerTest

from sru.srudrilldownadaptertest import SRUDrilldownAdapterTest, SRUTermDrilldownTest, SRUFieldDrilldownTest
from sru.srurecordupdatetest import SRURecordUpdateTest
from sru.srutest import SruTest
from sru.srwtest import SrwTest

#from oai.oaicomponenttest import OaiComponentTest
from oai.oaijazzlucenetest import OaiJazzLuceneTest, OaiJazzLuceneIntegrationTest
from oai.oaigetrecordtest import OaiGetRecordTest
from oai.oaiidentifytest import OaiIdentifyTest
from oai.oailistmetadataformatstest import OaiListMetadataFormatsTest
from oai.oailistsetstest import OaiListSetsTest
from oai.oailisttest import OaiListTest
from oai.oaimaintest import OaiMainTest
from oai.oaisinktest import OaiSinkTest
from oai.oaitooltest import OaiToolTest
from oai.oaiprovenancetest import OaiProvenanceTest
from oai.resumptiontokentest import ResumptionTokenTest

from xml2documenttest import Xml2DocumentTest  # --> Xml2Document only in use by OAI; deprecated; needs to be replaced
                                               #     when OAI is worked on next.

from xml_generic.lxml_based.crosswalktest import CrosswalkTest
from xml_generic.lxml_based.xsltcrosswalktest import XsltCrosswalkTest
from xml_generic.lxml_based.xmlxpathtest import XmlXPathTest
from xml_generic.lxml_based.xmlcomposetest import XmlComposeTest
from xml_generic.validatetest import ValidateTest

from dictionary.transformtest import TransformTest
from dictionary.alldotsplittedprefixestest import AllDotSplittedPrefixesTest
from dictionary.xpath2dicttest import XPath2DictTest

from resourcetest import ResourceTest
from helixtest import HelixTest

if __name__ == '__main__':
        unittest.main()
        os.system('find .. -name "*.pyc" | xargs rm -f')
