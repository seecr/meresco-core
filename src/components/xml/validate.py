#!/usr/bin/env python
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

from lxml.etree import parse, XMLSchema, XMLSchemaParseError
from os.path import join, abspath, dirname
from cStringIO import StringIO
from glob import glob

schemaLocation = join(abspath(dirname(__file__)), 'schemas')

rootSchema = '<?xml version="1.0" encoding="utf-8"?><xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">' \
 + '\n'.join('<xsd:import namespace="%s" schemaLocation="%s"/>' %
    (parse(xsd).getroot().get('targetNamespace'), xsd)
        for xsd in glob(join(schemaLocation,'*.xsd'))) \
+ '</xsd:schema>'

oai = parse(StringIO(rootSchema))

try:
    oaixsd = XMLSchema(oai)
except XMLSchemaParseError, e:
    print e.error_log.last_error
    raise

def validate(oaiResponse):
    oaixsd.validate(parse(oaiResponse))
    if oaixsd.error_log:
        return False, oaixsd.error_log.last_error
    else:
        return True, ''

def assertValid(oaiResponse):
    success, message = validate(oaiResponse)
    if not success:
        raise AssertionError(message)

def assertValidString(oaiResponseString):
    assertValid(StringIO(oaiResponseString))

if __name__ == '__main__':
    from sys import argv, exit
    args = argv[1:]
    if len(args) != 1:
        print "Validate a OAI response. "
        print "Usage: %s <response>" % argv[0]
        exit(1)
    success, message = validate(args[0])
    if success:
        print "Validation: OK"
    else:
        print "Validation: FAILED"
        print message
