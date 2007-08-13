## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
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

from cqlparser.cqlparser import parseString as parseCQL

from meresco.framework.observable import Observable

DEFAULT_MAXIMUM_TERMS = 10

def flatten(generators):
    for generator in generators:
        for line in generator:
            yield line

def generatorDecorate(before, data, after):
    beforeWritten = False
    for d in data:
        if not beforeWritten:
            yield before
            beforeWritten = True
        yield d
    if beforeWritten:
        yield after

class SRUDrillDownAdapter(Observable):

    def __init__(self, serverUrl):
        Observable.__init__(self)
        self.serverUrl = serverUrl

    def extraResponseData(self, webRequest, hits):
        return generatorDecorate(
            '<dd:drilldown xmlns:dd="%s/xsd/drilldown.xsd">' % self.serverUrl,
            flatten(self.all.extraResponseData(webRequest, hits)),
            "</dd:drilldown>")

    def echoedExtraRequestData(self, arguments):
        return generatorDecorate(
            '<dd:drilldown xmlns:dd="%s/xsd/drilldown.xsd">' % self.serverUrl,
            flatten(self.all.echoedExtraRequestData(arguments)),
            "</dd:drilldown>")


class SRUTermDrillDown(Observable):

    def extraResponseData(self, webRequest, hits):
        def splitTermAndMaximum(s):
            l = s.split(":")
            if len(l) == 1:
                return l[0], DEFAULT_MAXIMUM_TERMS
            return l[0], int(l[1])

        fieldsAndMaximums = webRequest._arguments.get('x-term-drilldown', [''])[0].split(",")
        fieldMaxTuples = (splitTermAndMaximum(s) for s in fieldsAndMaximums)

        if fieldsAndMaximums == [""]:
            raise StopIteration

        drillDownResults = self.any.drillDown(hits.docNumbers(), fieldMaxTuples)
        yield "<dd:term-drilldown>"
        for fieldname, termCounts in drillDownResults:
            yield '<dd:navigator name=%s>' % quoteattr(fieldname)
            for term, count in termCounts:
                yield '<dd:item count=%s>%s</dd:item>' % (quoteattr(str(count)), escape(str(term)))
            yield '</dd:navigator>'
        yield "</dd:term-drilldown>"

    def echoedExtraRequestData(self, arguments):
        argument = arguments.get('x-term-drilldown', [''])[0]
        if argument:
            yield "<dd:term-drilldown>"
            yield argument
            yield "</dd:term-drilldown>"

class SRUFieldDrillDown(Observable):

    def extraResponseData(self, webRequest, hits):
        query = webRequest._arguments.get('query', [''])[0]
        term = webRequest._arguments.get('x-field-drilldown', [''])[0]
        fields = webRequest._arguments.get('x-field-drilldown-fields', [''])[0].split(",")

        if not term or fields == [""]:
            raise StopIteration

        drillDownResults = self.drillDown(query, term, fields)

        yield "<dd:field-drilldown>"
        for field, count in drillDownResults:
            yield '<dd:field name=%s>%s</dd:field>' % (quoteattr(str(field)), escape(str(count)))
        yield "</dd:field-drilldown>"

    def drillDown(self, query, term, fields):
        for field in fields:
            hits = self.any.executeCQL(parseCQL('(%s) AND %s=%s' % (query, field, term)))
            yield field, len(hits)

    def echoedExtraRequestData(self, arguments):
        fieldDrillDown = arguments.get('x-field-drilldown', [''])[0]
        fieldDrillDownFields = arguments.get('x-field-drilldown-fields', [''])[0]
        if fieldDrillDown:
            yield "<dd:field-drilldown>"
            yield fieldDrillDown
            yield "</dd:field-drilldown>"
        if fieldDrillDownFields:
            yield "<dd:field-drilldown-fields>"
            yield fieldDrillDownFields
            yield "</dd:field-drilldown-fields>"
