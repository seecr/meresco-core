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

from time import mktime, gmtime
from meresco.framework import compose

from meresco.components.statistics import AggregatorException

class StatisticsXml(object):

    def __init__(self, statistics):
        self._statistics = statistics

    def handleRequest(self, RequestURI=None, *args, **kwargs):
        yield self._htmlHeader()
        arguments = self._parseArguments(RequestURI)

        try:
            fromTime = arguments.get("fromTime", None)
            if fromTime:
                fromTime = self._parseTime(fromTime[0])
            toTime = arguments.get("toTime", None)
            if toTime:
                toTime = self._parseTime(toTime[0])
        except ValueError:
            yield "<error>Invalid Time Format. Times must be of the format 1970-01-01T00:00:00Z or any shorter subpart.</error>"
            raise StopIteration
        try:
            maxResults = int(arguments.get("maxResults", [0])[0])
        except ValueError:
            yield "<error>maxResults must be number.</error>"
            raise StopIteration
        key = arguments.get("key", None)
        if not key:
            for stuff in self._listKeys():
                yield stuff
        else:
            key = tuple(key)
            for stuff in compose(self._query(fromTime, toTime, key, maxResults)):
                yield stuff

    def _htmlHeader(self):
        return """HTTP/1.0 200 Ok\r\nContent-Type: text/xml\r\n\r\n<?xml version="1.0" encoding="utf-8" ?>"""

    def _listKeys(self):
        yield "<statistics><header>%s</header><availableKeys>" % self._serverTime()
        for keys in self._statistics.listKeys():
            yield "<key>"
            for key in keys:
                yield "<keyElement>%s</keyElement>" % key
            yield "</key>"
        yield "</availableKeys></statistics>"

    def _query(self, fromTime, toTime, key, maxResults):

        try:
            data = self._statistics.get(key, fromTime, toTime).items()
        except KeyError, e:
            yield "<error>Unknown key: %s</error>" % str(key)
            raise StopIteration
        except AggregatorException, e:
            yield "<error>Statistics Aggregation Exception: %s</error>" % str(e)
            raise StopIteration
        if maxResults:
            data = self._sortedMaxed(data, maxResults)

        yield "<header>"
        yield self._serverTime()
        #fromTime
        #toTime
        yield "<key>"
        yield self._list(key, "keyElement")
        yield "</key>"
        yield "</header>"
        yield "<observations>"
        for value, count in data:
            yield "<observation>"
            yield self._list(value, "value")
            yield "<occurrences>%s</occurrences>" % count
            yield "</observation>"
        yield "</observations>"

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

    def _serverTime(self):
        return "<serverTime>%02d-%02d-%02dT%02d:%02d:%02dZ</serverTime>""" % gmtime()[:6]

    def _parseTime(self, s):
        result = []
        list = [(0, 4), (5, 7), (8, 10), (11, 13), (14, 16), (17, 19)]
        for (l, r) in list:
            if len(s) >= r:
                result.append((int(s[l:r])))
        return tuple(result)

