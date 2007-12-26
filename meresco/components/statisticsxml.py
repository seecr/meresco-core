


class StatisticsXml(object):

    def __init__(self, statistics):
        self._statistics = statistics

    def handleRequest(self, *args, **kwargs):
        yield "<statistics>"
        for key in self._statistics._keys:
            yield "<statistic>"
            yield "<query>"
            for keyPart in key:
                yield "<fieldName>%s</fieldName>" % keyPart
            yield "</query>"
            from time import time
            data = self._statistics.get(0, time() + 1, key)
            for value, count in data.items():
                yield "<result>"
                for keyPart in value:
                    yield "<fieldValue>%s</fieldValue>" % keyPart
                yield "<count>%s</count>" % count
                yield "</result>"
            yield "</statistic>"
        yield "</statistics>"