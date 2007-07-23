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
import sys
import traceback
import time
from meresco.legacy.pluginregistry import PluginRegistry
from meresco.framework.observable import Observable

def log(aString):
    try:
        sys.stdout.write(str(aString)+"\n")
        sys.stdout.flush()
    except:
        pass


class PluginAdapter(Observable): ###!!! No test for this backwards compatibilty component
    
    def __init__(self, configuration, searchInterfaces):
        Observable.__init__(self)
        self.configuration = configuration
    
        self.pluginRegistry = PluginRegistry(configuration)
        self.pluginRegistry.loadPlugins()
    
        self.searchInterfaces = searchInterfaces

    def getenv(self, key):
        return self.configuration.get(key,  None)
    
    def notify(self, aRequest):
        ignored, database, command, tail = (aRequest.path + '//').split('/',3)
        if database not in self.searchInterfaces.keys():
            return
        if not self.pluginRegistry.supportedCommand(command):
            return
        try:
            #assemble request
            aRequest.database = database
            aRequest.command = command
            aRequest.serverurl = 'http://%s:%s' % (self.getenv('server.host'), self.getenv('server.port'))
            aRequest.getenv = self.getenv
            aRequest.log = self.log
            aRequest.logException = self.logException

            
            plugin = self.pluginRegistry.create(command, aRequest, self.searchInterfaces[database])
            
            plugin.any = self.any
            plugin.all = self.all
            plugin.changed = self.changed
            
            plugin.process()
        except Exception, e:
            self.logException()
            aRequest.setResponseCode(e.errorCode)
            aRequest.setHeader('content-type', e.contentType)
            aRequest.write(str(e))
        
        
    def logException(self):
        self.log(traceback.format_exc())
        
    def log(self, something):
        log(str(something))
