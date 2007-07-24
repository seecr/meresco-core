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

from meresco.components.logobserver import LogObserver
from cStringIO import StringIO
from cq2utils.calltrace import CallTrace
from meresco.framework.observable import Observable

class LogObserverTest(TestCase):
    
    def testLogging(self):
        stream = StringIO()
        log = LogObserver(stream)
        
        class AnArgument:
            def __str__(self):
                return 'Looking for an argument.'
        argument = AnArgument()
        log.unknown('methodName', 'one', argument, 'three')
        
        time, line = stream.getvalue().split('\t',1)
        self.assertEquals('methodName - one\tLooking for an argument.\tthree\n', line)
        
    def testLoggingBySubclassing(self):
        stream = StringIO()
        arguments = []
        class MyLogObserver(LogObserver):
            def toString(self, *args):
                arguments.append(args)
                return 'toString'
        log = MyLogObserver(stream)
        
        log.unknown('methodName', 'one', 'two')
        
        time, line = stream.getvalue().split('\t',1)
        self.assertEquals('methodName - toString\n', line)
        self.assertEquals([('one','two')], arguments)
