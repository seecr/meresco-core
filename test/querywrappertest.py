import unittest
import tempfile
import os
import teddy.lucene
import shutil
import teddy.document
from core.index.querywrapper import QueryWrapper

class QueryWrapperTest(unittest.TestCase):
	
	def testUntokenizedQuery(self):
		self._luceneIndex._untokenizedTwinFieldnames = ['fieldname1']
		self._luceneIndex._drillDownFieldnames = ['fieldname1']
		self.add([('id1', {'fieldname1': 'contains space'})])
		hits = self.performQuery('fieldname1__untokenized__:"contains space"', untokenizedFieldNames = ['fieldname1__untokenized__'])
		self.assertEquals(1, len(hits))
		
	def testDefaultOperatorIsAND(self):
		self.add([('1', {'title': 'aap'}), ('2', {'title': 'noot'}), ('3', {'title': 'aap noot'})])
		self.assertEquals(['1', '3'], list(self.performQuery('aap')))
		self.assertEquals(['2', '3'], list(self.performQuery('noot')))
		self.assertEquals(['3'], list(self.performQuery('aap noot')))
	
	## general stuff:
	def add(self, documents):
		for aDocument in documents:
			myDocument = document.Document(aDocument[0])
			for field, value in aDocument[1].items():
				myDocument.addIndexedField(field, value)
			self._luceneIndex.addToIndex(myDocument)
		self._luceneIndex.reOpen()

	def setUp(self):
		self._tempdir = tempfile.gettempdir()+'/testing'
		self._directoryName = os.path.join(self._tempdir, 'lucene-index')
		self._luceneIndex = luceneindex.LuceneIndex(self._directoryName)
		
	def tearDown(self):
		if os.path.exists(self._tempdir):
			shutil.rmtree(self._tempdir)

	#note: changed wrt original
	def performQuery(self, queryString, sortBy = None, untokenizedFieldNames = []):
		queryWrapper = QueryWrapper(queryString, sortBy, untokenizedFieldNames = untokenizedFieldNames)
		hitsWrapper = self._luceneIndex.executeQuery(queryWrapper)
		return hitsWrapper

if __name__ == "__main__":
	unittest.main()