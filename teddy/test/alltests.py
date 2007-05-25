#!/usr/bin/env python
## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from os import system
system('rm -f *.pyc ../src/*.pyc')

from sys import path
path.append('../src')

import unittest

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

if __name__ == '__main__':
	unittest.main()

