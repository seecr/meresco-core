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

from meresco.framework.observable import Observable
from twisted.web import http
from twisted.internet import reactor
from sys import stdout, stderr
import traceback

class ObservableServer(Observable):
    def __init__(self, port):
        Observable.__init__(self)
        self.port = port
        
    def log(self, something):
        print >> stdout, something
        stdout.flush()
        
    def logError(self):
        print >> stderr, traceback.format_exc()
        stderr.flush()
    
    def run(self):
        class WebRequest(http.Request):
            
            def log(sself, something):
                self.log(something)
            
            def __str__(inner):
                return '\t'.join([inner.client.host, inner.method, inner.uri])
            
            def process(sself):
                try:
                    self.all.handleRequest(sself)
                except:
                    self.logError()
                sself.finish()
                
        class WebHTTPChannel(http.HTTPChannel):
            requestFactory = WebRequest
        class Factory(http.HTTPFactory):
            protocol = WebHTTPChannel
        
        factory = Factory()
        reactor.listenTCP(self.port, factory)
        self.log("Ready to rumble at %d\n" % self.port)
        reactor.run()
