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

from meresco.teddy.xml2document import Xml2Document, TEDDY_NS
from meresco.teddy.document import Document, IDFIELD
from amara import binderytools 
from meresco.framework.observable import Function
from cq2utils.component import Notification

class Xml2DocumentTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.converter = Xml2Document()
	
	def testId(self):
		document = self.converter.create('id', binderytools.bind_string('<fields/>').fields)
		self.assertTrue(isinstance(document, Document))
		luceneDoc = document._document
		self.assertEquals('id', luceneDoc.get(IDFIELD))
		
	def testIndexField(self):
		document = self.converter.create('id', binderytools.bind_string('<fields><tag>value</tag></fields>').fields)
		luceneDoc = document._document
		field = luceneDoc.getFields('tag')[0]
		self.assertEquals('value', field.stringValue())
		self.assertEquals('tag', field.name())
		self.assertEquals(True, field.isTokenized())
		
	def testIndexTokenizedField(self):
		document = self.converter.create('id', binderytools.bind_string('<fields xmlns:teddy="%s">\n<tag teddy:tokenize="false">value</tag></fields>' % TEDDY_NS).fields)
		luceneDoc = document._document
		field = luceneDoc.getFields('tag')[0]
		self.assertEquals('value', field.stringValue())
		self.assertEquals('tag', field.name())
		self.assertEquals(False, field.isTokenized())
		
	def testMultiLevel(self):
		document = self.converter.create('id', binderytools.bind_string("""<document xmlns:t="%s">
		<tag t:tokenize="false">value</tag>
		<lom>
			<general>
				<title>The title</title>
			</general>
		</lom>
	</document>""" % TEDDY_NS).document)
		luceneDoc = document._document
		field = luceneDoc.getFields('tag')[0]
		self.assertEquals('value', field.stringValue())
		self.assertEquals('tag', field.name())
		self.assertEquals(False, field.isTokenized())
		field = luceneDoc.getFields('lom.general.title')[0]
		self.assertEquals('The title', field.stringValue())
		self.assertEquals('lom.general.title', field.name())
		self.assertEquals(True, field.isTokenized())
		
	def testSkipFirstLevelForXmlFields(self):
		document = self.converter.create('id', binderytools.bind_string("""<document xmlns:t="%s">
		<xmlfields t:skip="true">
			<title>The title</title>
			<general><identifier>ID</identifier></general>
		</xmlfields>
	</document>""" % TEDDY_NS).document)
		luceneDoc = document._document
		fields = luceneDoc.getFields('title')
		self.assertTrue(fields != None)
		field = fields[0]
		self.assertEquals('The title', field.stringValue())
		self.assertEquals('title', field.name())
		self.assertEquals(True, field.isTokenized())
		field = luceneDoc.getFields('general.identifier')[0]
		self.assertEquals('ID', field.stringValue())
		self.assertEquals('general.identifier', field.name())
		self.assertEquals(True, field.isTokenized())
		
	def testIsObservable(self):
		notification = Notification()
		notification.id = "id_0"
		notification.method = "add"
		notification.payload = binderytools.bind_string('<fields/>').fields
		result = Function(self.converter)(notification)
		self.assertEquals("id_0", result.id)		
