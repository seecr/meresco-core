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

from merescocore.components.http import HandleRequestFilter
from merescocore.framework import be, Observable

class HandleRequestFilterTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.observer = CallTrace('Observer')

        self.usedKwargs = []
        def filterMethod(**kwargs):
            self.usedKwargs.append(kwargs)
            return self.result

        self.dna = be(
            (Observable(),
                (HandleRequestFilter(filterMethod),
                    (self.observer, )
                )
            )
        )

        
    def testPasses(self):
        self.result = True
        inputKwargs = dict(path='path', Method='GET')
        list(self.dna.all.handleRequest(**inputKwargs))

        self.assertEquals([('handleRequest', inputKwargs)], [(m.name, m.kwargs) for m in self.observer.calledMethods])
        self.assertEquals([inputKwargs], self.usedKwargs)

    def testYouShallNotPass(self):
        """Fly you fools!"""
        self.result = False
        inputKwargs = dict(path='path', Method='GET')
        list(self.dna.all.handleRequest(**inputKwargs))

        self.assertEquals([], [m.name for m in self.observer.calledMethods])
        self.assertEquals([inputKwargs], self.usedKwargs)