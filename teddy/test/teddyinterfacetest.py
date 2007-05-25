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
from cq2utils.calltrace import CallTrace

from queryserver.plugins.sruquery import SRUQuery
from teddyinterface import TeddyInterface, TeddyRecord, TeddyResult
from cStringIO import StringIO

class TeddyInterfaceTest(CQ2TestCase):
	def testTeddyInterface(self):
		luceneIndex = CallTrace('LuceneIndex')
		storage = CallTrace('Storage')
		luceneQuery = CallTrace('LuceneQuery')
		luceneIndex.returnValues['createQuery'] = luceneQuery
		
		face = TeddyInterface(luceneIndex, storage)
		
		query = SRUQuery('database', {})
		query.query = 'field=value'
		query.maximumRecords = 3
		query.startRecord = 5
		
		result = face.search(query)
		
		self.assertEquals(1, len(luceneIndex.calledMethods))
		self.assertEquals("createQuery('field:value', 4, 3, None, None)", str(luceneIndex.calledMethods[0]))
		
		self.assertTrue(isinstance(result, TeddyResult))
		
	def testTeddyResult(self):
		luceneQuery = CallTrace('LuceneQuery')
		luceneQuery.returnValues['perform'] = xrange(1,3)
		storage = CallTrace('Storage')
		
		result = TeddyResult(luceneQuery, storage)
		
		self.assertEquals(0, result.getNumberOfRecords())
		
		records = list(result.getRecords())
		self.assertEquals(2, len(records))
		recordOne = records[0]
		recordTwo = records[1]
		self.assertEquals(1, recordOne._documentId)
		self.assertEquals(2, recordTwo._documentId)
		
	def testTeddyRecord(self):
		storage = CallTrace('Storage')
		storageUnit = CallTrace('StorageUnit')
		storage.returnValues['getUnit'] = storageUnit
		
		openBoxCalls=[]
		def openBox(boxName, mode='r'):
			openBoxCalls.append(boxName)
			if boxName == 'test':
				return StringIO()
			elif boxName == 'fields':
				return StringIO()
			else:
				raise Exception(boxName)
		storageUnit.openBox = openBox
		
		record = TeddyRecord(1, storage)
		
		stream = CallTrace('Stream')
				
		record.writeDataOn('test', stream)
		self.assertEquals(1, len(storage.calledMethods))
		self.assertEquals('getUnit(1)', str(storage.calledMethods[0]))
		
		self.assertEquals(1, len(openBoxCalls))
		self.assertEquals('test', openBoxCalls[0])
		
		record.writeDataOn('fields', stream)
		self.assertEquals(2, len(storage.calledMethods))
		
		self.assertEquals(2, len(openBoxCalls))
		self.assertEquals('fields', openBoxCalls[1])
		

	def assertNextRecordPosition(self, expected, (count, offset, hitcount)):
		luceneQuery = CallTrace('LuceneQuery')
		storage = CallTrace('Storage')
			
		luceneQuery.returnValues['getCount'] = count
		luceneQuery.returnValues['getOffset'] = offset
		luceneQuery.returnValues['getHitCount'] = hitcount
		
		result = TeddyResult(luceneQuery, storage)
		
		self.assertEquals(expected, result.getNextRecordPosition())

	def testGetNextRecordPosition(self):
		self.assertNextRecordPosition(11, (10, 0, 12))
		self.assertNextRecordPosition(None, (10, 10, 12))
		self.assertNextRecordPosition(21, (10, 10, 22))
		self.assertNextRecordPosition(26, (20, 5, 50))
		
	def testWriteExtraResponseData(self):
		luceneQuery = CallTrace('LuceneQuery')
		luceneQuery.returnValues['getHitCount'] = 14
		storage = CallTrace('Storage')
		
		result = TeddyResult(luceneQuery, storage)
		
		stream = StringIO()
		
		result.writeExtraResponseDataOn(stream)
		
		self.assertEquals('<numberOfRecords>14</numberOfRecords>', stream.getvalue())
		
	def testCountField(self):
		luceneIndex = CallTrace('LuceneIndex')
		countFieldAnswer = [('a',2)]
		luceneIndex.returnValues['countField'] = countFieldAnswer
		storage = CallTrace('Storage')

		face = TeddyInterface(luceneIndex, storage)
		
		self.assertEquals(countFieldAnswer, face.countField('fieldname'))
		self.assertEquals(1, len(luceneIndex.calledMethods))
		self.assertEquals("countField('fieldname')", str(luceneIndex.calledMethods[0]))
		
	def testCatchException(self):
		storage = CallTrace('Storage')
		storageUnit = CallTrace('StorageUnit')
		storage.returnValues['getUnit'] = storageUnit
		
		openBoxCalls=[]
		def openBox(boxName, mode='r'):
			raise IOError()
		storageUnit.openBox = openBox
		
		record = TeddyRecord(1, storage)
		
		result = []
		for data in record.readData('boxName'):
			result.append(data)
		self.assertEquals([], result)
		
		stream = StringIO()
		record.writeDataOn('someschema', stream)
		self.assertEquals('', stream.getvalue())
		
	def testReset(self):
		luceneIndex = CallTrace('LuceneIndex')
		storage = CallTrace('Storage')
		
		face = TeddyInterface(luceneIndex, storage)
		
		face.reset()
		
		self.assertEquals(1, len(luceneIndex.calledMethods))
		self.assertEquals('reOpen()', str(luceneIndex.calledMethods[0]))
