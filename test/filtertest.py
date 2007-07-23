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

from cq2utils.calltrace import CallTrace
from cq2utils.component import Notification
from meresco.components.filter import Filter
from meresco.framework.observable import Observable

class FilterTest(TestCase):

    def testPassFilter(self):
        observer = CallTrace("Observer")

        subject = Filter(lambda x:x.method=='add')
        subject.addObserver(observer)

        notification = Notification(method='add')
        subject.notify(notification)
        self.assertEquals(1, len(observer.calledMethods))

    def testDontPassFilter(self):
        observer = CallTrace("Observer")

        subject = Filter(lambda x:x.method=='remove')
        subject.addObserver(observer)

        notification = Notification(method='add')
        subject.notify(notification)
        self.assertEquals(0, len(observer.calledMethods))

    def testAnotherPass(self):
        observer = CallTrace("Observer")
        observable = Observable()

        def aFilter(a, b=3, c=None):
            return b == 3
        subject = Filter(aFilter)
        subject.addObserver(observer)
        observable.addObserver(subject)
        arguments = []
        def notify(*args, **kwargs):
            arguments.append( (args, kwargs) )
        observer.notify = notify
        
        observable.changed(1)
        self.assertEquals(( (1,), {} ), arguments[0])
        observable.changed(c=3,a=1)
        self.assertEquals(( (), {'c':3,'a':1} ), arguments[1])
        
        
        
