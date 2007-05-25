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

from queryplugin import QueryPlugin, XML_CONTENT_TYPE, PluginException
from xml.sax.saxutils import escape as xmlEscape

ERROR_MESSAGE="""<?xml version="1.0" encoding="utf-8"?>
<error>Mandatory argument '%s' not specified.</error>"""

class FieldCountPlugin(QueryPlugin):
	def initialize(self):
		self.contentType = XML_CONTENT_TYPE

	def process(self):
		if not self._arguments.has_key('field'):
			raise PluginException(ERROR_MESSAGE % 'field')
		fieldName = self._arguments['field'][0]
		
		results = self.searchInterface.countField(fieldName)
		self.write('<?xml version="1.0" encoding="UTF-8"?>')
		self.write('<fieldcount count="%i">' % len(results))
		for k,v in results:
			k = xmlEscape(k)
			self.write(str('<item><value>%(k)s</value><count>%(v)i</count></item>' % locals()))
		self.write('</fieldcount>')

def registerOn(pluginRegistry):
	pluginRegistry.registerByCommand('fieldcount', FieldCountPlugin)
