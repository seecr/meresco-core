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

from cq2utils.cq2testcase import CQ2TestCase
from plugins.rssplugin import RSSPlugin, registerOn
from cq2utils.calltrace import CallTrace
from cStringIO import StringIO
from plugins.rssprofile import RSSTestProfile, readProfilesInDirectory
from tempfile import mkdtemp
from shutil import rmtree

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<description>Test description</description>
<link>http://www.example.org</link>
<title>Test title</title>
%s
</channel>
</rss>"""


RSSPROFILE = """rss.maximumRecords = 15
rss.sortKeys = 'sortField,,1'
channel.description = 'Test description'
channel.link = 'http://www.example.org'
channel.title = 'Test title'
def item(document):
	return [ ('title', document.xmlfields.dctitle),
		('link', document.xmlfields.identifier),
		('description', document.xmlfields.dcdescription)
	]
"""

class RSSPluginTest(CQ2TestCase):
	def setUp(self):
		self.tempdir = mkdtemp()
		fd = open('%s/default.rssprofile' % self.tempdir, 'w')
		try:
			fd.write(RSSPROFILE)
		finally:
			fd.close()
			
		self.buffer = StringIO()
		self.request = CallTrace('HTTPRequest')
		self.request.write = self.buffer.write
		self.request.getenv = self.getenv
		self.request.args = {}
		self.configuration = {'rss.profiles.directory': self.tempdir}
		self.searchinterface = MockSearchInterface()
		profiles = readProfilesInDirectory(self.tempdir)
		self.plugin = RSSPlugin(self.request, self.searchinterface, profiles)
	
	def tearDown(self):
		rmtree(self.tempdir)
	
	def getenv(self, key):
		return self.configuration[key]
	
	def testRegistry(self):
		registry = CallTrace('PluginRegistry')
		registry.returnValues['getenv'] = self.tempdir
		registerOn(registry)
		self.assertEquals(2, len(registry.calledMethods))
		self.assertEqual("getenv('rss.profiles.directory')", str(registry.calledMethods[0]))
		self.assertEquals("registerByCommand", registry.calledMethods[1].name)
		self.assertEquals("rss", registry.calledMethods[1].arguments[0])
		self.assertEquals(2, len(registry.calledMethods[1].arguments))
		
	def testNoResults(self):
		self.searchinterface.search_answer = MockSearchResult(0)

		self.plugin.process()
		
		self.assertEqualsWS(RSS % '', self.buffer.getvalue())
		
	def testError(self):
		self.request.args['query']= ['aQuery)']
		self.plugin.process()
		
		ERROR= """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>ERROR Test title</title>
<link>http://www.example.org</link>
<description>An error occurred 'Unexpected token after parsing, check for greediness ([)], cqlparser.cqlparser.CQL_QUERY(cqlparser.cqlparser.SCOPED_CLAUSE(cqlparser.cqlparser.SEARCH_CLAUSE(cqlparser.cqlparser.SEARCH_TERM('aQuery'))))).'</description>
</channel>
</rss>"""
		self.assertEqualsWS(ERROR, self.buffer.getvalue())
		
	def testResults(self):
		self.searchinterface.search_answer = MockSearchResult(1)
		self.searchinterface.search_answer.records = [MockSearchRecord('<document><xmlfields><dctitle>DC Title</dctitle></xmlfields></document>')]
		
		def write(something):
			self.assertEquals(str, type(something))
			self.buffer.write(something)
		self.request.write = write
		self.plugin.process()
		
		self.assertEqualsWS(RSS % """<item>
		<title>DC Title</title>
		<link></link>
		<description></description>
		</item>""", self.buffer.getvalue())
		
	def testWriteResultWithXmlEscaping(self):
		self.searchinterface.search_answer = MockSearchResult(1)
		self.searchinterface.search_answer.records = [MockSearchRecord('<document><xmlfields><dctitle>&amp;&lt;&gt;</dctitle></xmlfields></document>')]
		self.plugin.process()
		self.assertEqualsWS(RSS % """<item>
		<title>&amp;&lt;&gt;</title>
		<link></link>
		<description></description>
		</item>""", self.buffer.getvalue())
		
	def testMaximumRecords_and_SortKeys(self):
		self.request.args['query'] = ['aQuery']

		self.plugin.process()
		
		self.assertTrue(self.searchinterface.called)
		sruQuery = self.searchinterface.search_argument
		self.assertEquals('aQuery', sruQuery.query)
		self.assertEquals(1, sruQuery.startRecord)
		self.assertEquals(15, sruQuery.maximumRecords)
		self.assertEquals('sortField', sruQuery.sortBy)
		self.assertEquals(True, sruQuery.sortDirection)
		
	def testNoSortKeysInProfile(self):
		self.plugin._profiles['default'].sortKeys = lambda: None
		self.request.args['query'] = ['aQuery']

		self.plugin.process()
		sruQuery = self.searchinterface.search_argument
		self.assertEquals(None, sruQuery.sortBy)
		self.assertEquals(None, sruQuery.sortDirection)
		
	def testSortKeysAndMaximumRecordsOverridden(self):
		self.request.args.update({'query': ['aQuery'], 'maximumRecords':['12'], 'sortKeys':['dctitle,,0']})

		self.plugin.process()
		
		sruQuery = self.searchinterface.search_argument
		self.assertEquals('aQuery', sruQuery.query)
		self.assertEquals(1, sruQuery.startRecord)
		self.assertEquals(12, sruQuery.maximumRecords)
		self.assertEquals('dctitle', sruQuery.sortBy)
		self.assertEquals(False, sruQuery.sortDirection)
		
		
	def testSelectOtherProfile(self):
		profile = RSSTestProfile()
		profile._channel.extraTitle = 'Other'
		profile._item = lambda x: [('title', 'othertitle')]
		self.plugin._profiles['otherprofile'] = profile
		self.request.args.update({'query': ['aQuery'], 'x-rss-profile':['otherprofile']})
		self.searchinterface.search_answer = MockSearchResult(1)
		self.searchinterface.search_answer.records = [MockSearchRecord('<fields/>')]
		
		self.plugin.process()
		
		otherrss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Test title</title>
<link>http://www.example.org</link>
<description>Test description</description>
<extraTitle>Other</extraTitle>
<item>
		<title>othertitle</title>
</item>
</channel>
</rss>"""
		self.assertEqualsWS(otherrss, self.buffer.getvalue())
	
	def testResultsWithNoSuchProfile(self):
		self.searchinterface.search_answer = MockSearchResult(1)
		self.searchinterface.search_answer.records = [MockSearchRecord('<document><xmlfields><dctitle>DC Title</dctitle></xmlfields></document>')]
		self.request.args['x-rss-profile']= ['not-there']
		
		self.plugin.process()
		
		self.assertEqualsWS(RSS % """<item>
		<title>DC Title</title>
		<link></link>
		<description></description>
		</item>""", self.buffer.getvalue())

class MockSearchInterface:
	def __init__(self):
		self.called = False
		self.search_answer = MockSearchResult(0)
	def search(self, sruQuery):
		self.called = True
		self.search_argument = sruQuery
		return self.search_answer

class MockSearchResult:
	def __init__(self, size):
		self._size = size
		self.records = []
	def getNumberOfRecords(self):
		return self._size
	
	def getRecords(self):
		return self.records
	
	def getNextRecordPosition(self):
		"""
		Returns the recordPosition for the next batch.
		Returns None if no more records available.
		"""
		return self._size + 1
	
class MockSearchRecord:
	def __init__(self, content):
		self.content = content
		
	def readData(self, dataName):
		return StringIO(self.content)
		

