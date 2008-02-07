from meresco.framework import Observable

from lxml.etree import parse, XSLT, _ElementTree

class XsltCrosswalk(Observable):

    def __init__(self, xslFileList):
        Observable.__init__(self)
        self._xslts = [XSLT(parse(open(xslFile))) for xslFile in xslFileList]

    def _convert(self, xmlSource):
        result = xmlSource
        for xslt in self._xslts:
            result = xslt(result)
        return result

    def _detectAndConvert(self, anObject):
        result = anObject
        if type(anObject) == _ElementTree:
            result = self._convert(anObject)
        print ">>>", type(result)
        return result

    def unknown(self, method, *args, **kwargs):
        newArgs = [self._detectAndConvert(arg) for arg in args]
        newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
        return self.all.unknown(method, *newArgs, **newKwargs)
