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

from xml.sax.saxutils import quoteattr, escape

from meresco.framework.observable import Observable
from meresco.framework.generatorutils import compose

class SimpleXmlServer(Observable):

    def handleRequest(self, port=None, Client=None, RequestURI=None, Method=None, Headers=None, **kwargs):
        yield 'HTTP/1.0 200 Ok\r\n'
        yield "Content-Type: text/xml\r\n"
        yield "\r\n"

        #temp solution:
        parts = RequestURI.split('?')
        if len(parts) == 2:
            fields = parts[1].split('/')
        if len(parts) != 2 or fields == [""]:
            raise StopIteration

        fieldMaxTuples = ((s, 0) for s in fields)

        drilldownResults = self.any.drilldown(None, fieldMaxTuples)

        yield "<termDrilldown>"
        for fieldname, termCounts in drilldownResults:
            yield '<field name=%s>' % quoteattr(fieldname)
            for term, count in termCounts:
                yield '<term><text>'
                yield escape(term)
                yield '</text><count>'
                yield str(count)
                yield '</count></term>'
            yield '</field>'
        yield "</termDrilldown>"
