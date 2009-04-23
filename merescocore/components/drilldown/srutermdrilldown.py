
from merescocore.framework import Observable, decorateWith
from drilldown import DRILLDOWN_HEADER, DRILLDOWN_FOOTER, DEFAULT_MAXIMUM_TERMS
from xml.sax.saxutils import escape as xmlEscape, quoteattr

class SRUTermDrilldown(Observable):
    def __init__(self, sortedByTermCount=False):
        Observable.__init__(self)
        self._sortedByTermCount = sortedByTermCount
                
    @decorateWith(DRILLDOWN_HEADER, DRILLDOWN_FOOTER)
    def extraResponseData(self, cqlAbstractSyntaxTree=None, x_term_drilldown=None, **kwargs):
        if x_term_drilldown == None or len(x_term_drilldown) != 1:
            return
        def splitTermAndMaximum(s):
            l = s.split(":")
            if len(l) == 1:
                return l[0], DEFAULT_MAXIMUM_TERMS, self._sortedByTermCount
            return l[0], int(l[1]), self._sortedByTermCount

        fieldsAndMaximums = x_term_drilldown[0].split(",")
        fieldMaxTuples = (splitTermAndMaximum(s) for s in fieldsAndMaximums)

        if fieldsAndMaximums == [""]:
            raise StopIteration

        drilldownResults = self.any.drilldown(
            self.any.docsetFromQuery(cqlAbstractSyntaxTree),
            fieldMaxTuples)
        yield "<dd:term-drilldown>"
        for fieldname, termCounts in drilldownResults:
            yield '<dd:navigator name=%s>' % quoteattr(fieldname)
            for term, count in termCounts:
                yield '<dd:item count=%s>%s</dd:item>' % (quoteattr(str(count)), xmlEscape(str(term)))
            yield '</dd:navigator>'
        yield "</dd:term-drilldown>"
        
    @decorateWith(DRILLDOWN_HEADER, DRILLDOWN_FOOTER)
    def echoedExtraRequestData(self, x_term_drilldown=None, **kwargs):
        if x_term_drilldown and len(x_term_drilldown) == 1:
            yield "<dd:term-drilldown>"
            yield xmlEscape(x_term_drilldown[0])
            yield "</dd:term-drilldown>"