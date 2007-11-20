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

from xml.sax.saxutils import escape as xmlEscape
from xml.sax import SAXParseException

from cgi import parse_qs
from urlparse import urlsplit

from amara.binderytools import bind_string

from cq2utils.wrappers import wrapp

from meresco.framework import Observable, compose
from meresco.components.sru.sruquery import SRUQuery, SRUQueryException
from meresco.components.http import utils as httputils

from cqlparser.cqlparser import parseString as parseCQL

class BadRequestException(Exception):
    pass

class Rss(Observable):

    def __init__(self, profiles):
        Observable.__init__(self)
        self._profiles = profiles

    def handleRequest(self, RequestURI='', **kwargs):
        yield httputils.okRss

        yield """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>"""

        arguments = self._parseUri(RequestURI)
        profile = self._getProfile(arguments)

        try:
            arguments, recordSchema = self._parseArguments(profile, arguments)
            query = self._createSruQuery(arguments)
        except BadRequestException, e:
            channel = profile.channel() #if you get this far...
            yield '<title>ERROR %s</title>' % xmlEscape(getattr(channel, 'title', ''))
            yield '<link>%s</link>' % xmlEscape(getattr(channel, 'link', ''))
            yield "<description>An error occurred '%s'</description>" % xmlEscape(str(e))
            yield """</channel></rss>"""
            raise StopIteration()

        channel = profile.channel()
        for tagname, value in channel.listAttributes():
            value = xmlEscape(value)
            yield '<%(tagname)s>%(value)s</%(tagname)s>' % locals()

        #try:
        for data in compose(self._yieldResults(profile, recordSchema, query)):
            yield data
        #except:
            #print
            #pass ###!!!!!!!! some nice way to deal with errors in this late stage...

        yield """</channel>"""
        yield """</rss>"""

    def _parseUri(self, RequestURI):
        Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
        return parse_qs(Query)

    def _getProfile(self, arguments):
        profileName = arguments.get('x-rss-profile', ['default'])[0]
        return self._profiles.get(profileName, self._profiles.get('default'))

    def _parseArguments(self, profile, arguments):
        """Or rather: set some defaults, based on profile"""
        if not arguments.has_key('sortKeys') and profile.sortKeys():
            arguments['sortKeys'] = [profile.sortKeys()]
        if not arguments.has_key('maximumRecords'):
            arguments['maximumRecords'] = [str(profile.maximumRecords())]
        recordSchema = profile.recordSchema()
        return arguments, recordSchema

    def _createSruQuery(self, arguments):
        try:
            query = SRUQuery(arguments)
        except SRUQueryException, e:
            raise BadRequestException(e)
        return query

    def _yieldResults(self, profile, recordSchema, sruQuery):
        """Bad name, taken from SRU"""
        hits = self.any.executeCQL(parseCQL(sruQuery.query), sruQuery.sortBy,  sruQuery.sortDirection)

        SRU_IS_ONE_BASED = 1 #And our RSS plugin is closely based on SRU
        start = sruQuery.startRecord - SRU_IS_ONE_BASED

        for recordId in hits[start: start + sruQuery.maximumRecords]:
            yield self._yieldResult(profile, recordSchema, recordId)

    def _yieldResult(self, profile, recordSchema, recordId):
        s = "".join(self.all.yieldRecord(recordId, recordSchema))
        rootNode = wrapp(bind_string(s).childNodes[0])

        yield '<item>'
        for rssname, value in profile.item(rootNode):
            value = xmlEscape(str(value))
            yield '<%(rssname)s>%(value)s</%(rssname)s>' % locals()
        yield '</item>'
