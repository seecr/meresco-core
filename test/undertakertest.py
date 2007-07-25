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

from unittest import TestCase
from meresco.framework.observable import Observable
from meresco.components.undertaker import Undertaker
from amara.binderytools import bind_string

class UnderTakerTest(TestCase):
    
    def setUp(self):
        self.undertaker = Undertaker()
        self.undertaker.addObserver(self)
        self.addArgs = []
        self.deletePartArgs = []
        self.somethingElseCalled = False
    
    def testAdd(self):
        self.undertaker.add("AN_ID", "A_PARTNAME", 'A PAYLOAD (is in reality amary object)')
        self.assertEquals([('AN_ID', "A_PARTNAME", 'A PAYLOAD (is in reality amary object)')], self.addArgs)
        self.assertEquals([('AN_ID', '__tombstone__')], self.deletePartArgs)
        
    def testDelete(self):
        self.undertaker.delete('AN_ID')
        self.assertEquals(0, len(self.deletePartArgs))
        self.assertEquals(('AN_ID', '__tombstone__'), self.addArgs[0][:2])
        self.assertEquals("<__tombstone__/>", self.addArgs[0][2].xml())
    
    def testPassAlongEverythingElse(self):
        class MyObservable(Observable):
            def somethingElse(self):
                return self.do.somethingElse()
        root = MyObservable()
        root.addObserver(self.undertaker)
        self.assertFalse(self.somethingElseCalled)
        root.somethingElse()
        self.assertTrue(self.somethingElseCalled)
        
    def add(self, *args):
        """self shunt"""
        self.addArgs.append(args)
        
    def deletePart(self, id, partName):
        self.deletePartArgs.append((id, partName))

    def somethingElse(self):
        self.somethingElseCalled = True