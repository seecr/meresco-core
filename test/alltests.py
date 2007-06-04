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

sys.path.append("../src")

import unittest

from servertest import ServerTest
from sruplugintest import SRUPluginTest
from srwplugintest import SRWPluginTest
from xmlfileplugintest import XMLFilePluginTest
from pluginregistrytest import PluginRegistryTest
from sruquerytest import SRUQueryTest
from fieldcountplugintest import FieldCountPluginTest
from rssplugintest import RSSPluginTest
from rssprofiletest import RSSProfileTest
from logtest import LogTest
from oaiidentifytest import OaiIdentifyTest
from oaivalidatortest import OaiValidatorTest
from oaigetrecordtest import OaiGetRecordTest
from oailisttest import OaiListTest
from oaisinktest import OaiSinkTest
from oaicomponenttest import OaiComponentTest
from oaitooltest import OaiToolTest
from resetplugintest import ResetPluginTest
from stampcomponenttest import StampComponentTest
from portaltest import PortalTest
from configurationtest import ConfigurationTest
from documenttest import DocumentTest
from lucenetest import LuceneTest
from srurecordupdateplugintest import SRURecordUpdatePluginTest
#from stresstest import StressTest #TJ/JJ: TODO rewrite stresstest.
from teddyinterfacetest import TeddyInterfaceTest
from teddyinterfaceconstructortest import TeddyInterfaceConstructorTest
from teddygrowlservertest import TeddyGrowlServerTest
from xml2documenttest import Xml2DocumentTest
from storagecomponenttest import StorageComponentTest
from indexcomponenttest import IndexComponentTest
from fields2xmlcomponenttest import Fields2XmlComponentTest
from logcomponenttest import LogComponentTest
from venturitest import VenturiTest
from xmlpumptest import XmlPumpTest
from hitstest import HitsTest
from querywrappertest import QueryWrapperTest
from xslicetest import XSliceTest
from undertakertest import UnderTakerTest
from oailistmetadataformatstest import OaiListMetadataFormatsTest
from partscomponenttest import PartsComponentTest

if __name__ == '__main__':
        unittest.main()

