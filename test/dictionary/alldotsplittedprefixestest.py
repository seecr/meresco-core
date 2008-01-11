## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
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
from meresco.components.dictionary.alldotsplittedprefixes import AllDotSplittedPrefixes
from meresco.components.dictionary import Transform, DocumentField

from cq2utils import CallTrace

import unittest

class AllDotSplittedPrefixesTest(unittest.TestCase):

    def testBasicBehavior(self):
        component = AllDotSplittedPrefixes()
        observer = CallTrace()
        component.addObserver(observer)
        component.addField("id", DocumentField('root.zero.one', 'field contents', additionalParam="propagated"))
        self.assertEquals(3, len(observer.calledMethods))

        self.assertEquals(DocumentField('root', 'field contents', additionalParam="propagated"), observer.calledMethods[0].arguments[1])
        self.assertEquals(DocumentField('root.zero', 'field contents', additionalParam="propagated"), observer.calledMethods[1].arguments[1])
        self.assertEquals(DocumentField('root.zero.one', 'field contents', additionalParam="propagated"), observer.calledMethods[2].arguments[1])


