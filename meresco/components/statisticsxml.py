from cgi import parse_qs
from urlparse import urlsplit

from time import mktime
from meresco.framework import compose

class StatisticsXml(object):

    def __init__(self, statistics):
        self._statistics = statistics

    def handleRequest(self, RequestURI=None, *args, **kwargs):
        arguments = self._parseArguments(RequestURI)
        beginDay = self._parseDay(arguments.get("beginDay", ["1970-01-01"])[0])
        endDay = self._parseDay(arguments.get("endDay", ["2030-12-31"])[0], endDay=True)
        maxResults = int(arguments.get("maxResults", [0])[0])
        key = arguments.get("key", None)
        if not key:
            return self._listKeys()
        if key:
            key = tuple(key)
        return compose(self._query(beginDay, endDay, key, maxResults))

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

    def _query(self, beginDay, endDay, key, maxResults):
        yield self._htmlHeader()

        try:
            data = self._statistics.get(beginDay, endDay, key).items()
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

    def _parseDay(self, s, endDay=False):
        year = int(s[:4])
        mon = int(s[5:7])
        day = int(s[8:10])
        hour = endDay and 23 or 0
        min = endDay and 59 or 0
        sec = endDay and 59 or 0
        return int(mktime((year, mon, day, hour, min, sec, 0, -1, 0))) + self._correctForLocalTime()

    def _correctForLocalTime(self):
        return -1 * int(mktime((1970, 1,  1, 0, 0, 0, 0, -1, 0)))