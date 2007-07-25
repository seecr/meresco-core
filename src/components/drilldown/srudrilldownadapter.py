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

from xml.sax.saxutils import quoteattr, escape

from meresco.framework.observable import Observable

class SRUDrillDownAdapter(Observable):
    def extraResponseData(self, webRequest, hits):
        fieldsAndMaximums = webRequest._arguments.get('x-meresco-drilldown', [''])[0].split(",")
        fieldMaxTuples = ((s, int(i)) for (s, i) in (tuple(s.split(":")) for s in fieldsAndMaximums))
        
        if fieldsAndMaximums == [""]:
            raise StopIteration
        yield "<drilldown>" #I think this should reflect the original name
        drillDownResults = self.any.drillDown(hits.docNumbers(), fieldMaxTuples)
        for fieldname, termCounts in drillDownResults:
            yield '<field name=%s>' % quoteattr(fieldname)
            for term, count in termCounts:
                yield '<value count=%s>%s</value>' % (quoteattr(str(count)), escape(str(term)))
            yield '</field>'
        yield "</drilldown>"
