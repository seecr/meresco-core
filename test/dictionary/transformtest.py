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
from meresco.components.dictionary.transform import CleanSplit, years
from meresco.components.dictionary import Transform, DocumentField

from cq2utils import CallTrace

import unittest

class TransformTest(unittest.TestCase):

    def testBasicBehavior(self):
        observer = CallTrace("observer")
        transform = Transform('some.source', 'target', CleanSplit(';'))
        transform.addObserver(observer)
        transform.addField(DocumentField('some.source', 'some;thing'))
        self.assertEquals(2, len(observer.calledMethods))

        self.assertEquals(DocumentField('target', 'some'), observer.calledMethods[0].arguments[0])
        self.assertEquals(DocumentField('target', 'thing'), observer.calledMethods[1].arguments[0])


    def testYears(self):
        self.assertEquals([], years('garbage'))
        self.assertEquals(['2000'], years('2000'))
        self.assertEquals(['2000', '2001'], years('2000-2001'))
        self.assertEquals(['2000'], years('2000-01-01'))
        self.assertEquals(['2000'], years('2000-01-01T23:32:12Z'))
