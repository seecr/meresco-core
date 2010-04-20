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

from cq2utils import CQ2TestCase, CallTrace
from os.path import join

from meresco.components.contextset import ContextSet, ContextSetException, ContextSetList
from StringIO import StringIO

class ContextSetTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        stream = StringIO("""
# test contextset file
query.field1\tactualfield1
field1 actualfield1
field2  actualfield2
field2    actualotherfield2

""")
        self.set = ContextSet('test', stream)

    def testLookup(self):
        self.assertEquals('test', self.set.name)
        self.assertEquals('actualfield1', self.set.lookup('test.query.field1'))
        self.assertEquals('actualfield1', self.set.lookup('test.field1'))
        self.assertEquals('actualfield2', self.set.lookup('test.field2'))
        self.assertEquals('nosuchfield', self.set.lookup('nosuchfield'))
        self.assertEquals('test.nosuchfield', self.set.lookup('test.nosuchfield'))
        self.assertEquals('otherset.field', self.set.lookup('otherset.field'))

    def testReverseLookup(self):
        self.assertEquals('test.query.field1', self.set.reverseLookup('actualfield1'))
        self.assertEquals('test.field2', self.set.reverseLookup('actualfield2'))
        self.assertEquals('test.field2', self.set.reverseLookup('actualotherfield2'))
        self.assertEquals('nosuchfield', self.set.reverseLookup('nosuchfield'))

    def testLookupInList(self):
        setlist = ContextSetList()
        setlist.add(ContextSet('set1', StringIO("field\tactualfield\nfield1\tactualfield1")))
        setlist.add(ContextSet('set2', StringIO("field\tactualfield\nfield2\tactualfield2")))
        self.assertEquals('actualfield', setlist.lookup('set1.field'))
        self.assertEquals('actualfield', setlist.lookup('set2.field'))
        self.assertEquals('actualfield2', setlist.lookup('set2.field2'))
        self.assertEquals('set2.field2', setlist.reverseLookup('actualfield2'))
        self.assertEquals('set1.field1', setlist.reverseLookup('actualfield1'))
        self.assertEquals('set1.field', setlist.reverseLookup('actualfield'))
        self.assertEquals('set1.thisDoesNotExist', setlist.reverseLookup('set1.thisDoesNotExist'))
        self.assertEquals('noreversefield', setlist.reverseLookup('noreversefield'))
        self.assertEquals('unsupportedset.field3', setlist.lookup('unsupportedset.field3'))


