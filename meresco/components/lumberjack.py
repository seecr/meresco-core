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

from threading import Event

from meresco.framework.observable import Observable

from PyLucene import PythonThread

class Lumberjack:
    """We'll leave the test as an exercise to the reader"""
    
    def __init__(self, root, observersFactory):
        self.root = root
        self.observersFactory = observersFactory
        self.event = Event()
        thread = PythonThread(target=self.justKeepChopping)
        thread.setDaemon(True)
        thread.start()
        
    def unknown(self, methodName, *args):
        self.event.set()
            
    def justKeepChopping(self):
        while True:
            self.event.wait()
            self.event.clear()
            self.chop()
            
    def chop(self):
        atomicWorkAround = Observable()
        atomicWorkAround.addObservers(self.observersFactory())
        self.root._observers = atomicWorkAround._observers
