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
from meresco.components.setscomponent import SetsComponent
from cq2utils.component import Notification
from amara.binderytools import bind_string

class SetsComponentTest(TestCase):
    
    def setUp(self):
        self.notifications = []
    
    def testSets(self):
        notification = Notification("add", "id_1")
        notification.sets = [("one:two:three", "Three Piggies"), ( "one:two:four", "Four Chickies")]
        setsComponent = SetsComponent()
        setsComponent.addObserver(self)
        setsComponent.notify(notification)
        
        setsNotification = Notification("add", "id_1", "__sets__", bind_string("""<__sets__><set><setSpec>one:two:three</setSpec><setName>Three Piggies</setName></set><set><setSpec>one:two:four</setSpec><setName>Four Chickies</setName></set></__sets__>"""))
        
        self.assertEquals([(setsNotification, )], self.notifications)
        
    def testNoSets(self):
        notification = Notification("add", "id_1")
        
        setsComponent = SetsComponent()
        setsComponent.addObserver(self)
        setsComponent.notify(notification)

        self.assertEquals([], self.notifications)
        
    def testFlattenedSets(self):
        notification = Notification("add", "id_1")
        notification.sets = [("one:two:three", "Three Piggies"), ("one:two:four", "Four Chickies")]
        setsComponent = SetsComponent(self)
        setsComponent.notify(notification)
        
        setsNotification = Notification("add", "id_1", "__set_membership__", bind_string("""<__set_membership__><set %(tokenized)s>one:two:three</set><set %(tokenized)s>one:two</set><set %(tokenized)s>one:two:four</set><set %(tokenized)s>one</set></__set_membership__>""" % {"tokenized": 'xmlns:teddy="http://www.cq2.nl/teddy" teddy:tokenize="false"'}).childNodes[0])
        
        self.assertEquals([(setsNotification, )], self.notifications)

    def testSetsDatabase(self):
        notification = Notification("add", "id_1")
        notification.sets = [("one:two:three", "Three Piggies"), ( "one:two:four", "Four Chickies")]
        setsComponent = SetsComponent(None, self)
        setsComponent.notify(notification)
        
        self.assertEquals(2, len(self.notifications))
        
        one = Notification("add", "one:two:three", "set", bind_string("""<set><setSpec>one:two:three</setSpec><setName>Three Piggies</setName></set>""").set)
        
        two = Notification("add", "one:two:four", "set", bind_string("""<set><setSpec>one:two:four</setSpec><setName>Four Chickies</setName></set>""").set)
        
        self.assertEquals((one, ), self.notifications[0])
        self.assertEquals((two, ), self.notifications[1])

    def notify(self, *args):
        self.notifications.append(args)
    
