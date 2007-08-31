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

from cStringIO import StringIO
from cq2utils.cq2testcase import CQ2TestCase

from lxml.etree import parse, _ElementTree

from meresco.components.xml_generic.validate import Validate, ValidateException
from meresco.framework import Observable

class ValidateTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.validate = Validate()
        self.exception = None
        self.args = None
        class Interceptor:
            def unknown(inner, message, *args, **kwargs):
                self.args = args
                yield None
            def logException(inner, anException):
                self.exception = anException

        self.validate.addObserver(Interceptor())
        self.observable = Observable()
        self.observable.addObserver(self.validate)

    def testOneInvalid(self):
        invalidXml = '<lom xmlns="http://ltsc.ieee.org/xsd/LOM_this_should_not_work"/>'
        try:
            self.observable.any.someMethod(parse(StringIO(invalidXml)))
            self.fail('must raise exception')
        except ValidateException:
            pass
        self.assertEquals("<string>:1:ERROR:SCHEMASV:SCHEMAV_CVC_ELT_1: Element '{http://ltsc.ieee.org/xsd/LOM_this_should_not_work}lom': No matching global declaration available for the validation root.", str(self.exception))

    def testAssertValidString(self):
        s = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
<responseDate>2007-01-01T00:00:00Z</responseDate>
<request verb="Identify">url</request>
<Identify>
    <repositoryName>The Repository Name</repositoryName>
    <baseURL>http://base.example.org/url</baseURL>
    <protocolVersion>2.0</protocolVersion>
    <adminEmail>info@cq2.nl</adminEmail>
    <earliestDatestamp>1970-01-01T00:00:00Z</earliestDatestamp>
    <deletedRecord>no</deletedRecord>
    <granularity>YYYY-MM-DDThh:mm:ssZ</granularity>
  </Identify>
</OAI-PMH>"""
        self.observable.any.callSomething(parse(StringIO(s)))
        self.assertEquals(None, self.exception)
        self.assertEquals(_ElementTree, type(self.args[0]))

    def testAssertInvalidString(self):
        invalid = '<OAI-PMH/>'
        try:
            self.observable.any.message(parse(StringIO(invalid)))
            self.fail('must raise exception')
        except ValidateException, e:
            pass
        self.assertEquals("<string>:1:ERROR:SCHEMASV:SCHEMAV_CVC_ELT_1: Element 'OAI-PMH': No matching global declaration available for the validation root.", str(self.exception))
