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
from cgi import parse_qs
from urlparse import urlsplit

from time import mktime
from meresco.framework import compose

class StatisticsXml(object):

    def __init__(self, statistics):
        self._statistics = statistics

    def handleRequest(self, RequestURI=None, *args, **kwargs):
        arguments = self._parseArguments(RequestURI)
        fromTime = arguments.get("fromTime", None)
        if fromTime:
            fromTime = self._parseTime(fromTime[0])
        toTime = arguments.get("toTime", None)
        if toTime:
            toTime = self._parseTime(toTime[0])
        maxResults = int(arguments.get("maxResults", [0])[0])
        key = arguments.get("key", None)
        if not key:
            return self._listKeys()
        if key:
            key = tuple(key)
        return compose(self._query(fromTime, toTime, key, maxResults))

    def _htmlHeader(self):
        return "HTTP/1.0 200 Ok\r\nContent-Type: text/xml\r\n\r\n"

    def _listKeys(self):
        yield self._htmlHeader()

        yield "<queries>"
        for keys in self._statistics.listKeys():
            yield "<query>"
            for key in keys:
                yield "<key>%s</key>" % key
            yield "</query>"
        yield "</queries>"

    def _query(self, fromTime, toTime, key, maxResults):
        yield self._htmlHeader()

        try:
            data = self._statistics.get(key, fromTime, toTime).items()
        except KeyError, e:
            yield "<error>Unknown key: %s</error>" % str(key)
            raise StopIteration
        if maxResults:
            data = self._sortedMaxed(data, maxResults)

        yield "<statistic>"
        yield "<query>"
        yield self._list(key, "key")
        yield "</query>"
        for value, count in data:
            yield "<result>"
            yield self._list(value, "value")
            yield "<count>%s</count>" % count
            yield "</result>"
        yield "</statistic>"

    def _sortedMaxed(self, data, maxResults):
        def cmp((leftValue, leftCount), (rightValue, rightCount)):
            if not leftCount == rightCount:
                return rightCount - leftCount
            return rightValue - leftValue
        return sorted(data, cmp=cmp)[:maxResults]

    def _list(self, list, tagName):
        if not list:
            yield "<%s>%s</%s>" % (tagName, "None", tagName)
        else:
            for e in list:
                yield "<%s>%s</%s>" % (tagName, e, tagName)

    def _parseArguments(self, RequestURI):
        Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
        arguments = parse_qs(Query)
        return arguments

    def _parseTime(self, s):
        result = []
        list = [(0, 4), (5, 7), (8, 10), (11, 13), (14, 16), (17, 19)]
        for (l, r) in list:
            if len(s) >= r:
                result.append((int(s[l:r])))
        return tuple(result)

