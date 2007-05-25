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

from os import system
system('rm -f *.pyc ../src/*.pyc')

from sys import path
path.append('../src')

from unittest import main
from cq2utils.cq2testcase import CQ2TestCase
from lucene import LuceneIndex
from document import Document

class StressTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self._luceneIndex = LuceneIndex(self.tempdir)
		myDocument = Document('0123456789')
		myDocument.addIndexedField('title', 'een titel')
		self._luceneIndex.addToIndex(myDocument)
		self._luceneIndex.reOpen()
		
	def tearDown(self):
		self._luceneIndex = None
		CQ2TestCase.tearDown(self)

	def testLotsOfQueries(self):
		query = self._luceneIndex.createQuery('title:titel')
		result = list(query.perform())
		self.assertEquals(1,len(result))
		def f():
			for i in xrange(10000):
				list(self._luceneIndex.createQuery('title:titel').perform())
		from cq2utils.profile import profile
		profile(f, 'stresstest2', True)
		
if __name__ == "__main__":
	main()
