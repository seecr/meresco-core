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

from cq2utils.cq2testcase import CQ2TestCase

from meresco.teddy.teddyinterfaceconstructor import construct
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
