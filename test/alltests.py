#!/usr/bin/env python
## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
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

import os, sys
os.system('find .. -name "*.pyc" | xargs rm -f')

from glob import glob
for path in glob('../deps.d/*'):
    sys.path.insert(0, path)
sys.path.insert(0, "..")

import unittest

from bitarraytest import BitArrayTest
from bitmatrixtest import BitMatrixTest
from contextsettest import ContextSetTest
from documenttest import DocumentTest
from drilldownfilterstest import DrillDownFiltersTest
from drilldowntest import DrillDownTest
from fieldcountplugintest import FieldCountPluginTest
from fields2xmlcomponenttest import Fields2XmlComponentTest
from generatorutilstest import GeneratorUtilsTest
from hitstest import HitsTest
from logcomponenttest import LogComponentTest
from logobservertest import LogObserverTest
from logtest import LogTest
from lucenerawdocsetstest import LuceneRawDocSetsTest
from lucenetest import LuceneTest
from observabletest import ObservableTest
from rssplugintest import RSSPluginTest
from rssprofiletest import RSSProfileTest

from sru.srudrilldownadaptertest import SRUDrillDownAdapterTest, SRUTermDrillDownTest, SRUFieldDrillDownTest
from sru.sruplugintest import SRUPluginTest
from sru.sruquerytest import SRUQueryTest
from sru.srurecordupdatetest import SRURecordUpdateTest
from sru.srwplugintest import SRWPluginTest
from storagecomponenttest import StorageComponentTest
from teddygrowlservertest import TeddyGrowlServerTest
from venturitest import VenturiTest
from xml2documenttest import Xml2DocumentTest
from xmlfileplugintest import XMLFilePluginTest
from xmlpumptest import XmlPumpTest
from xslicetest import XSliceTest

from legacy.teddyinterfaceconstructortest import TeddyInterfaceConstructorTest
from legacy.teddyinterfacetest import TeddyInterfaceTest
from legacy.configurationtest import ConfigurationTest
from legacy.portaltest import PortalTest
from legacy.pluginregistrytest import PluginRegistryTest

from oai.oaijazzlucenetest import OaiJazzLuceneTest
from oai.oaijazzlucenetest import OaiJazzLuceneIntegrationTest

#from oai.oaicomponenttest import OaiComponentTest
from oai.oaigetrecordtest import OaiGetRecordTest
from oai.oaiidentifytest import OaiIdentifyTest
from oai.oailistmetadataformatstest import OaiListMetadataFormatsTest
from oai.oailistsetstest import OaiListSetsTest
from oai.oailisttest import OaiListTest
from oai.oaimaintest import OaiMainTest
from oai.oaisinktest import OaiSinkTest
from oai.oaitooltest import OaiToolTest
from oai.resumptiontokentest import ResumptionTokenTest

from xml_generic.lxml_based.crosswalktest import CrosswalkTest
from xml_generic.lxml_based.crosswalktestbase import CrosswalkTestBase
from xml_generic.validatetest import ValidateTest

if __name__ == '__main__':
        unittest.main()
        os.system('find .. -name "*.pyc" | xargs rm -f')
