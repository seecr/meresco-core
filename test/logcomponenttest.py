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

from meresco.components.logcomponent import LogComponent
from meresco.core.observable import Observable
from cq2utils import CallTrace, CQ2TestCase

class LogComponentTest(CQ2TestCase):

    def testLog(self):
        observable = Observable()
        logger = LogComponent(self.tempfile)
        observable.addObserver(logger)
        observable.any.method("anId", "partName", "payload", kwarg="kwarg", count=10)
        oneline = open(self.tempfile).read().strip()
        time, message = oneline.split('\t')
        self.assertEquals("notify: method, anId, partName, payload, count=10, kwarg='kwarg'", message)
        self.assertTrue(float(time))

