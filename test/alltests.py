#!/usr/bin/env python
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

if os.environ.get('PYTHONPATH', '') == '':
    sys.path.insert(0, "..")

import unittest

from accumulatetest import AccumulateTest
from contextsettest import ContextSetTest
from cqlparsetreetolucenequerytest import CqlParseTreeToLuceneQueryTest
from documenttest import DocumentTest
from drilldownfilterstest import DrilldownFiltersTest
from drilldowntest import DrilldownTest
from generatorutilstest import GeneratorUtilsTest
from hitstest import HitsTest
from incnumbermaptest import IncNumberMapTest
from logcomponenttest import LogComponentTest
from logobservertest import LogObserverTest
from lucenerawdocsetstest import LuceneRawDocSetsTest
from lucenetest import LuceneTest
from observabletest import ObservableTest
from storagecomponenttest import StorageComponentTest
from storageharvestertest import StorageHarvesterTest
from rsstest import RssTest
from rssitemtest import RssItemTest
from statisticstest import StatisticsTest
from statisticsxmltest import StatisticsXmlTest
from teddygrowlservertest import TeddyGrowlServerTest
from venturitest import VenturiTest
from xml2documenttest import Xml2DocumentTest
from xmlpumptest import XmlPumpTest
from xslicetest import XSliceTest

from http.fileservertest import FileServerTest

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

from xml_generic.lxml_based.crosswalktest import CrosswalkTest
from xml_generic.lxml_based.xsltcrosswalktest import XsltCrosswalkTest
from xml_generic.lxml_based.xmlxpathtest import XmlXPathTest
from xml_generic.lxml_based.xmlcomposetest import XmlComposeTest
from xml_generic.validatetest import ValidateTest

from dictionary.transformtest import TransformTest
from dictionary.alldotsplittedprefixestest import AllDotSplittedPrefixesTest
from dictionary.xml2dicttest import Xml2DictTest

if __name__ == '__main__':
        unittest.main()
        os.system('find .. -name "*.pyc" | xargs rm -f')
