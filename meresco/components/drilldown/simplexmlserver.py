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
from cgi import parse_qs
from urlparse import urlsplit

from PyLucene import BooleanQuery, BooleanClause, Term, TermQuery

class SimpleXmlServer(Observable):

    def handleRequest(self, port=None, Client=None, RequestURI=None, Method=None, Headers=None, **kwargs):
        yield 'HTTP/1.0 200 Ok\r\n'
        yield "Content-Type: text/xml; charset=utf-8\r\n"
        yield "\r\n"

        past, future = self._parseRequestURI(RequestURI)

        if past:
            query = self._createLuceneQuery(past)
            docNumbers = self.any.executeQuery(query).docNumbers()
        else:
            docNumbers = None

        fieldMaxTuples = ((s, 10) for s in future)
        drilldownResults = self.any.drilldown(docNumbers, fieldMaxTuples)

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

    def _createLuceneQuery(self, args):
        args = [s.split("=", 1) for s in args]
        #untokenized hier terug laten komen is een vieze vette hack natuurlijk.
        termQueries = [TermQuery(Term(field + "__untokenized__", value)) for field, value in args]
        result = BooleanQuery()
        for termQuery in termQueries:
            result.add(termQuery, BooleanClause.Occur.MUST)
        return result

    def _parseRequestURI(self, RequestURI):
        scheme, netloc, path, query, fragment = urlsplit(RequestURI)
        args = parse_qs(query)
        past = args.get('past', None)
        future = args['future']
        return past, future
