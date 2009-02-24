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

from cq2utils import CQ2TestCase, CallTrace
from merescocore.components import CQLConversion
from merescocore.framework import Observable, be
from cqlparser import parseString


class CQLConversionTest(CQ2TestCase):
    
    def testCQLContextSetConversion(self):
        observer = CallTrace('observer')
        o = be((Observable(),
            (CQLConversion(lambda ast:parseString('anotherQuery')),
                (observer,)
            )
        ))
        o.do.whatever(parseString('afield = value'))
        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals('whatever', observer.calledMethods[0].name)
        self.assertEquals((parseString('anotherQuery'),), observer.calledMethods[0].args)

    def testCQLCanConvert(self):
        c = CQLConversion(lambda ast: ast)
        self.assertTrue(c._canConvert(parseString('field = value')))
        self.assertFalse(c._canConvert('other object'))

    def testCQLConvert(self):
        converter = CallTrace('Converter')
        converter.returnValues['convert'] = parseString('ast')
        c = CQLConversion(converter.convert)
        self.assertEquals(parseString('ast'), c._convert(parseString('otherfield = value')))
        self.assertEquals(['convert'], [m.name for m in converter.calledMethods])
