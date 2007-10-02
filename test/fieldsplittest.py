## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school.
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
from meresco.components.fieldsplit import FieldSplit, CleanSplit, years

from cq2utils import CallTrace

from amara.binderytools import bind_string
import unittest

class FieldSplitTest(unittest.TestCase):

    def testBasicBehavior(self):
        observer = CallTrace("observer")
        node = bind_string("<a><b>1; 2; 3</b></a>").a
        fieldsplit = FieldSplit('a.b', CleanSplit(';'))
        fieldsplit.addObserver(observer)
        fieldsplit.add("id", "partname", node)
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals("<a><b>1</b><b>2</b><b>3</b></a>", method.args[2].xml())


    def testYears(self):
        self.assertEquals([], years('garbage'))
        self.assertEquals(['2000'], years('2000'))
        self.assertEquals(['2000', '2001'], years('2000-2001'))
        self.assertEquals(['2000'], years('2000-01-01'))
        self.assertEquals(['2000'], years('2000-01-01T23:32:12Z'))
