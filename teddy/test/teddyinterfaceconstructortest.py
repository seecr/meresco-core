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

from cq2utils.cq2testcase import CQ2TestCase

from teddyinterfaceconstructor import construct
import os

def writeFile(filename, content):
	f = open(filename, 'w')
	try:
		f.write(content)
	finally:
		f.close()

CONTENTS = """<configuration><storage>%s</storage><lucene>%s</lucene></configuration>"""

class TeddyInterfaceConstructorTest(CQ2TestCase):
	def testConstruct(self):
		for db in ['a', 'b']:
			writeFile(self.tempdir + '/%s.database' % db, CONTENTS % (self.tempdir + '/index/storage_%s' % db, self.tempdir + '/index/lucene_%s' % db ))
		config = {'teddy.config.dir': self.tempdir}
		self.assertTrue(not os.path.isdir(self.tempdir + '/index'))
		interfaces = construct(config)
		self.assertEquals(set(['a','b']), set(interfaces.keys()))
		self.assertEquals(set(['storage_a', 'storage_b', 'lucene_a', 'lucene_b']), set(os.listdir(self.tempdir + '/index')))
