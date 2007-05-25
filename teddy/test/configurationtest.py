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

import unittest
import cStringIO
import configuration
import tempfile
import os

config = """<?xml version="1.0"?>
<configuration>
	<storage>x</storage>
	<lucene>y</lucene>
</configuration>
"""

class ConfigurationTest(unittest.TestCase):

	def testReading(self):
		myConfiguration = configuration.Configuration()
		myConfiguration.readFrom(cStringIO.StringIO(config))
		
		self.assertEquals(myConfiguration.getStorage(), 'x')
		self.assertEquals(myConfiguration.getLucene(), 'y')

	def testReadFromFile(self):
		fd,fname = tempfile.mkstemp(text=True)
		try:
			fd = open(fname,'w')
			fd.write(config)
		finally:
			fd.close()
		
		try:
			myConfiguration = configuration.Configuration()
			myConfiguration.readFromFile(fname)
			self.assertEquals(myConfiguration.getStorage(), 'x')
			self.assertEquals(myConfiguration.getLucene(), 'y')
		finally:
			os.remove(fname)
