#!/usr/bin/env python
## begin license ##
#
#    QueryServer is a framework for handling search queries.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of QueryServer.
#
#    QueryServer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    QueryServer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QueryServer; if not, write to the Free Software
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
from oailistrecordstest import OaiListRecordsTest
from oaisinktest import OaiSinkTest
from oaicomponenttest import OaiComponentTest
from oaitooltest import OaiToolTest
from resetplugintest import ResetPluginTest
from stampcomponenttest import StampComponentTest
from portaltest import PortalTest

if __name__ == '__main__':
        unittest.main()

