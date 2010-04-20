## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
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

from lxml.etree import parse, XMLSchema, XMLSchemaParseError, _ElementTree, tostring
from StringIO import StringIO

from meresco.core import Observable

class ValidateException(Exception):
    pass

class Validate(Observable):
    def __init__(self, schemaPath):
        Observable.__init__(self)
        try:
            self._schema = XMLSchema(parse(open(schemaPath)))
        except XMLSchemaParseError, e:
            print e.error_log.last_error
            raise


    def unknown(self, *args, **kwargs):
        allArguments = list(args) + kwargs.values()
        for arg in allArguments:
            if type(arg) == _ElementTree:
                toValidate = parse(StringIO(tostring(arg, pretty_print=True)))
                self._schema.validate(toValidate)
                if self._schema.error_log:
                    exception = ValidateException(self._schema.error_log.last_error)
                    self.do.logException(exception)
                    raise exception
        return self.all.unknown(*args, **kwargs)

def assertValid(xmlString, schemaPath):
    schema = XMLSchema(parse(open(schemaPath)))
    toValidate = parse(StringIO(xmlString))
    schema.validate(toValidate)
    if schema.error_log:
        for nr, line in enumerate(tostring(toValidate, encoding="utf-8", pretty_print=True).split('\n')):
            print nr+1, line
        raise AssertionError(str(schema.error_log))
