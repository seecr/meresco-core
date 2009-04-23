## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
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

from xml.sax.saxutils import quoteattr, escape

from cqlparser.cqlparser import parseString as parseCQL

from merescocore.framework.observable import Observable
from merescocore.framework.generatorutils import decorate

from weightless import compose

DEFAULT_MAXIMUM_TERMS = 10

DRILLDOWN_HEADER = """<dd:drilldown
    xmlns:dd="http://namespace.meresco.org/drilldown"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://namespace.meresco.org/drilldown http://namespace.drilldown.org/xsd/drilldown.xsd">"""
DRILLDOWN_FOOTER = "</dd:drilldown>"

class decorateWith:
    def __init__(self, before, after):
        self.before = before
        self.after = after
    def __call__(self, g):
        def newg(*args, **kwargs):
            return decorate(self.before,
                            g(*args, **kwargs),
                            self.after)
        return newg
    

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
                yield '<dd:item count=%s>%s</dd:item>' % (quoteattr(str(count)), escape(str(term)))
            yield '</dd:navigator>'
        yield "</dd:term-drilldown>"

    @decorateWith(DRILLDOWN_HEADER, DRILLDOWN_FOOTER)
    def echoedExtraRequestData(self, x_term_drilldown=None, **kwargs):
        if x_term_drilldown and len(x_term_drilldown) == 1:
            yield "<dd:term-drilldown>"
            yield escape(x_term_drilldown[0])
            yield "</dd:term-drilldown>"


class SRUFieldDrilldown(Observable):
    @decorateWith(DRILLDOWN_HEADER, DRILLDOWN_FOOTER)
    def extraResponseData(self, query=None, x_field_drilldown=None, x_field_drilldown_fields=None, **kwargs):
        if not x_field_drilldown or len(x_field_drilldown) != 1:
            return
        if not x_field_drilldown_fields or len(x_field_drilldown_fields) != 1:
            return
        
        term = x_field_drilldown[0]
        fields = x_field_drilldown_fields[0].split(',')

        drilldownResults = self.drilldown(query, term, fields)
        yield "<dd:field-drilldown>"
        for field, count in drilldownResults:
            yield '<dd:field name=%s>%s</dd:field>' % (quoteattr(escape(str(field))), escape(str(count)))
        yield "</dd:field-drilldown>"

    def drilldown(self, query, term, fields):
        for field in fields:
            cqlString = '(%s) AND %s=%s' % (query, field, term)
            total, recordIds = self.any.executeCQL(cqlAbstractSyntaxTree=parseCQL(cqlString))
            yield field, total

    @decorateWith(DRILLDOWN_HEADER, DRILLDOWN_FOOTER)
    def echoedExtraRequestData(self, x_field_drilldown=None, x_field_drilldown_fields=None, **kwargs):
        if x_field_drilldown and len(x_field_drilldown) == 1:
            yield "<dd:field-drilldown>"
            yield escape(x_field_drilldown[0])
            yield "</dd:field-drilldown>"
        if x_field_drilldown_fields and len(x_field_drilldown_fields) == 1:
            yield "<dd:field-drilldown-fields>"
            yield escape(x_field_drilldown_fields[0])
            yield "</dd:field-drilldown-fields>"
