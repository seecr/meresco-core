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
from unittest import TestCase
from cq2utils import CallTrace

from StringIO import StringIO

from timerfortestsupport import TimerForTestSupport
from meresco.components.documentqueue import DocumentQueue

class DocumentQueueTest(TestCase):
    
    def testQueue(self):
        queue = DocumentQueue('storage', TimerOff(), 1)
        self.assertEquals(None, queue._dequeue())
        queue._enqueue(0)
        queue._enqueue(1)
        self.assertEquals(0, queue._dequeue())
        self.assertEquals(1, queue._dequeue())
        self.assertEquals(None, queue._dequeue())
        
        for x in range(10000):
            queue._enqueue(x)
        for x in range(10000):
            self.assertEquals(x, queue._dequeue())
        self.assertEquals(None, queue._dequeue())

    def testAdd(self):
        storageComponent = CallTrace("Storage Component")
        storageComponent.returnValues['getStream'] = StringIO('a document')
        observer = CallTrace("Observer")
        queue = DocumentQueue(storageComponent, TimerOff(), 1)
        queue.addObserver(observer)
        queue.add('id0', 'partname', 'a document')
        self.assertEquals("add", storageComponent.calledMethods[0].name)
        self.assertEquals(['id0', 'queued', 'a document'], storageComponent.calledMethods[0].arguments)
        
        queue._tick()
        self.assertEquals("getStream", storageComponent.calledMethods[1].name)
        self.assertEquals(['id0', 'queued'], storageComponent.calledMethods[1].arguments)
        
        self.assertEquals("add", observer.calledMethods[0].name)
        self.assertEquals(['id0', 'unknown', 'a document'], observer.calledMethods[0].arguments)
        
    def testDelete(self):
        storageComponent = CallTrace("Storage Component")
        observer = CallTrace("Observer")
        queue = DocumentQueue(storageComponent, TimerOff(), 1)
        queue.addObserver(observer)
        queue.delete('id0')
        self.assertEquals("deletePart", storageComponent.calledMethods[0].name)
        self.assertEquals(['id0', 'queued'], storageComponent.calledMethods[0].arguments)
        
        queue._tick()
        
        self.assertEquals("delete", observer.calledMethods[0].name)
        self.assertEquals(['id0'], observer.calledMethods[0].arguments)


class TimerOff(object):
    def addTimer(self, time, callback):
        pass
    def removeTimer(self, token):
        pass