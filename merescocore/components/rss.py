## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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

from xml.sax.saxutils import escape as xmlEscape
from xml.sax import SAXParseException

from cgi import parse_qs
from urlparse import urlsplit

from amara.binderytools import bind_string

from cq2utils.wrappers import wrapp

from merescocore.framework import Observable, compose
from merescocore.components.sru.sruquery import SRUQuery, SRUQueryException
from merescocore.components.http import utils as httputils

from cqlparser.cqlparser import parseString as parseCQL

class BadRequestException(Exception):
    pass

class Rss(Observable):

    def __init__(self, title, description, link, **sruArgs):
        Observable.__init__(self)
        self._title = title
        self._description = description
        self._link = link
        self._sortKeys = sruArgs.get('sortKeys', None)
        self._maximumRecords = sruArgs.get('maximumRecords', 10)

    def handleRequest(self, RequestURI='', **kwargs):
        yield httputils.okRss
        yield """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>"""
        try:
            Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
            arguments = parse_qs(Query)
            sortKeys = arguments.get('sortKeys', [self._sortKeys])[0]
            maximumRecords = arguments.get('maximumRecords', [self._maximumRecords])[0]
            query = arguments.get('query', [''])[0]
            if not query:
                raise SRUQueryException("MANDATORY parameter 'query' not supplied or empty")
            sruQueryArguments = {
                'query': [query],
                'maximumRecords': [str(maximumRecords)],
            }
            if sortKeys != None:
                sruQueryArguments['sortKeys'] = [sortKeys]
            sruQuery = SRUQuery(sruQueryArguments)
        except (SRUQueryException,BadRequestException), e:
            yield '<title>ERROR %s</title>' % xmlEscape(self._title)
            yield '<link>%s</link>' % xmlEscape(self._link)
            yield "<description>An error occurred '%s'</description>" % xmlEscape(str(e))
            yield """</channel></rss>"""
            raise StopIteration()

        yield '<title>%s</title>' % xmlEscape(self._title)
        yield '<description>%s</description>' % xmlEscape(self._description)
        yield '<link>%s</link>' % xmlEscape(self._link)

        for data in compose(self._yieldResults(sruQuery)):
            yield data

        yield """</channel>"""
        yield """</rss>"""


    def _yieldResults(self, sruQuery):
        SRU_IS_ONE_BASED = 1 #And our RSS plugin is closely based on SRU
        start = sruQuery.startRecord - SRU_IS_ONE_BASED

        total, hits = self.any.executeCQL(cqlAbstractSyntaxTree=parseCQL(sruQuery.query), start=start, stop=start + sruQuery.maximumRecords, sortBy=sruQuery.sortBy,  sortDescending=sruQuery.sortDescending)

        for recordId in hits:
            yield self.any.getRecord(recordId)
