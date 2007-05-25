#!/usr/bin/env python
## begin license ##
#
#    QueryServer is a framework for handling search queries.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of QueryServer.
#
#    QueryServer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    QueryServer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QueryServer; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from lxml.etree import parse, XMLSchema, XMLSchemaParseError
from os.path import join, abspath, dirname
from cStringIO import StringIO


schemaLocation = join(abspath(dirname(__file__)), 'data')
# Create an XSD validator to validate the XSD
xsdxsd = XMLSchema(parse(join(schemaLocation, 'XMLSchema.xsd')))
# Parse the XSD and validate it as XSD
oai = parse(join(schemaLocation, 'OAI-PMH.xsd'))
xsdxsd.validate(oai)
# Create an XSD validator to validate the XML instance
oaixsd = XMLSchema(oai)

def validate(oaiResponse):
	# Parse the XML and validate it
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
