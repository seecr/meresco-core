from cgi import parse_qs
from urlparse import urlsplit

from time import mktime

class StatisticsXml(object):

    def __init__(self, statistics):
        self._statistics = statistics

    def handleRequest(self, RequestURI=None, *args, **kwargs):
        arguments = self._parseArguments(RequestURI)
        beginDay = self._parseDay(arguments.get("beginDay", "1970-01-01"))
        endDay = self._parseDay(arguments.get("endDay", "2030-12-31"))
        key = arguments.get("key", None)

        yield "<statistics>"
        for key in self._statistics._keys:
            yield "<statistic>"
            yield "<query>"
            for keyPart in key:
                yield "<fieldName>%s</fieldName>" % keyPart
            yield "</query>"
            data = self._statistics.get(beginDay, endDay, key)
            for value, count in data.items():
                yield "<result>"
                for keyPart in value:
                    yield "<fieldValue>%s</fieldValue>" % keyPart
                yield "<count>%s</count>" % count
                yield "</result>"
            yield "</statistic>"
        yield "</statistics>"

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
        return int(mktime((year, mon, day, hour, min, sec, 0, 0, 0)))