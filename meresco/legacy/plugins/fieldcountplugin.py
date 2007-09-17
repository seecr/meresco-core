## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
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

from queryplugin import QueryPlugin, XML_CONTENT_TYPE, PluginException
from xml.sax.saxutils import escape as xmlEscape

ERROR_MESSAGE="""<?xml version="1.0" encoding="utf-8"?>
<error>Mandatory argument '%s' not specified.</error>"""

from warnings import warn
warn("DEPRECATED: FieldCountPlugin works exclusivly with PyLucene == 2.0.0. Remove lucene.countfield and related stuff, or fix it, or create an new implementation with drilldown.")

class FieldCountPlugin(QueryPlugin):
    #Refactordirection: this should start to use the drilldown countfield functionality.

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
