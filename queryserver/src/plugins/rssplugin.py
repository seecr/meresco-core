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

from queryplugin import QueryPlugin
from sruplugin import SRUPlugin as TeddySRUPlugin
from amara import binderytools
from cq2utils.wrappers import wrapp
from xml.sax.saxutils import escape as xmlEscape
from rssprofile import readProfilesInDirectory
from sruquery import SRUQuery, SRUQueryException
from xml.sax import SAXParseException

DEFAULT_PROFILE_NAME = 'default'
PROFILE_ARGUMENT = 'x-rss-profile'

class RSSPlugin(QueryPlugin):
	def __init__(self, aRequest, searchInterface, profiles):
		QueryPlugin.__init__(self, aRequest, searchInterface)
		self._profiles = profiles
		
	def initialize(self):
		self.xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>'
		self.contentType = 'application/rss+xml'
	
	def process(self):
		if not self._arguments.has_key('sortKeys') and self.profile().sortKeys():
			self._arguments['sortKeys'] = [self.profile().sortKeys()]
		if not self._arguments.has_key('maximumRecords'):
			self._arguments['maximumRecords'] = [str(self.profile().maximumRecords())]
			
		try:
			sruquery = SRUQuery(self._database, self._arguments)
		except SRUQueryException, e:
			self.handleException(e)
			return
		
		searchResult = self.searchInterface.search(sruquery)

		self._startResults(searchResult.getNumberOfRecords())
		for record in searchResult.getRecords():
			self._writeResult(record)
		self._endResults()
	
	def handleException(self, exception):
		self.write(self.xmlHeader)
		self.write('<rss version="2.0">')
		self.write('<channel>')
		channel = self.profile().channel()
		self.write('<title>ERROR %s</title>' % xmlEscape(getattr(channel, 'title', '')))
		self.write('<link>%s</link>' % xmlEscape(getattr(channel, 'link', '')))
		self.write("<description>An error occurred '%s'</description>" % xmlEscape(str(exception)))
		self.write('</channel>')
		self.write('</rss>')
	
	def _writeRSSHeader(self):
		channel = self.profile().channel()
		for tagname, value in channel.listAttributes():
			value = xmlEscape(value)
			self.write('<%(tagname)s>%(value)s</%(tagname)s>' % locals())
		
	def _startResults(self, aNumber):
		self.write(self.xmlHeader)
		self.write('<rss version="2.0">')
		self.write('<channel>')
		self._writeRSSHeader()
	
	def _endResults(self):
		self.write('</channel>')
		self.write('</rss>')
		
	def profile(self):
		profileName = self._arguments.get(PROFILE_ARGUMENT,[DEFAULT_PROFILE_NAME])[0]
		return self._profiles.get(profileName, self._profiles.get(DEFAULT_PROFILE_NAME))
	
	def _writeResult(self, aRecord):
		try:
			document = wrapp(binderytools.bind_stream(aRecord.readData('document'))).document
		except SAXParseException:
			self._request.logException()
			return
		
		self.write('<item>')
		for rssname, value in self.profile().item(document):
			value = xmlEscape(str(value))
			self.write('<%(rssname)s>%(value)s</%(rssname)s>' % locals())
		self.write('</item>')
		
def sortDict(aDictionary):
	return sorted(aDictionary.items(), lambda (k1,v1),(k2,v2):cmp(k1,k2))

def registerOn(aRegistry):
	profiles = readProfilesInDirectory(aRegistry.getenv('rss.profiles.directory'))
	aRegistry.registerByCommand('rss', lambda aRequest, searchInterface: RSSPlugin(aRequest, searchInterface, profiles))
