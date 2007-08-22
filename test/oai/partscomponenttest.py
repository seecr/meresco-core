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
from meresco.components.oai.partscomponent import PartsComponent
from cq2utils.calltrace import CallTrace
from cq2utils.component import Notification
from amara.binderytools import bind_string
from StringIO import StringIO

class PartsComponentTest(TestCase):
    
    def setUp(self):
        self.box = StringIO("<__parts__><part>partA</part></__parts__>")
        self.unit = CallTrace("Unit", returnValues = {"hasBox": True, "openBox": self.box})
        self.storage = CallTrace("Storage", returnValues = {"getUnit": self.unit})
        self.subject = PartsComponent(self.storage, ["partA", "partB"])
        self.subject.addObserver(self)
        self.notifications = []
    
    def testNonMaintainedParts(self):
        notification = Notification("add", "id_1", "nonMaintainedPart", "payload")
        self.subject.notify(notification)
        self.assertEquals([(notification, )], self.notifications)
        
    def testAdd(self):
        notification = Notification("add", "id_1", "partB", "payload")
        self.subject.notify(notification)
        
        partNotification = Notification("add", "id_1", "__parts__", bind_string('<__parts__ xmlns:teddy="http://www.cq2.nl/teddy"><part  teddy:tokenize="false">partA</part><part teddy:tokenize="false">partB</part></__parts__>').__parts__)
        self.assertEquals(2, len(self.notifications))
        self.assertEquals((notification, ), self.notifications[0])
        self.assertEquals((partNotification, ), self.notifications[1], self.notifications[1][0].payload.xml())
    
    def testDelete(self):
        notification = Notification("delete", "id_1", "partA", "payload")
        self.subject.notify(notification)
        
        partNotification = Notification("add", "id_1", "__parts__", bind_string("<__parts__></__parts__>").__parts__)
        self.assertEquals([
            (notification, ),
            (partNotification, )], self.notifications)
    
    def notify(self, *args):
        self.notifications.append(args)
