#!/usr/bin/env python
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

from twisted.internet import reactor
from twisted.web import http

import sys
import traceback
import time
from meresco.legacy.plugins.queryplugin import PluginException
from meresco.legacy.pluginregistry import PluginRegistry
from os import getpid
from cq2utils import config

startTime = time.time()
queries = 0

def increaseQueries():
    global queries
    
    queries = queries + 1

def getQueryCount():
    global queries
    
    return queries

def getStartTime():
    global startTime
    
    return startTime

def log(aString):
    try:
        sys.stdout.write(str(aString)+"\n")
        sys.stdout.flush()
    except:
        pass

class WebRequest(http.Request):

    def __init__(self, configuration, pluginRegistry, searchInterfaces, *args):
        http.Request.__init__(self, *args)
        self.configuration = configuration
        self.pluginRegistry = pluginRegistry
        self.searchInterfaces = searchInterfaces

    def getenv(self, key):
        return self.configuration.get(key,  None)
        
    def getHandler(self):
        return self.handlers().get(self.path, self.handleDefault)
    
    def handlers(self):
        return {'/status': self.handleStatus, '/favicon.ico': self.handleFavicon}

    def handleStatus(self):
        self.setResponseCode(200)
        self.setHeader('content-type', 'text/plain')
        self.write("Queries: %s\n" % getQueryCount())
        self.write("StartTime: %s\n" % time.ctime(getStartTime()))
        self.write("CurrentTime: %s\n" % time.asctime(time.localtime()))
                
    def handleFavicon(self):
        self.setResponseCode(404)
        self.setHeader('content-type', 'text/plain')
        self.write('404: file not found')

    def handleDatabaseNotFound(self):
        self.setResponseCode(400)
        self.setHeader('content-type', 'text/plain')
        self.write('400 Bad Request: database "%s" not found.' % self.database)
    
    def handleDefault(self):
        try:
            if self.database not in self.searchInterfaces.keys():
                self.handleDatabaseNotFound()
                return
            plugin = self.pluginRegistry.create(self.command, self, self.searchInterfaces[self.database])
            plugin.process()
        except PluginException, e:
            self.logException()
            self.setResponseCode(e.errorCode)
            self.setHeader('content-type', e.contentType)
            self.write(str(e))
                        
    def logException(self):
        self.log(traceback.format_exc())
        
    def log(self, something):
        log(str(something))
    
    def _initializeRequestSettings(self):
        ignored, self.database, self.command, tail = (self.path + '//').split('/',3)
        self.serverurl = 'http://%s:%s' % (self.getenv('server.host'), self.getenv('server.port'))

    def process(self):
        self._initializeRequestSettings()
        try:
            self.getHandler()()
        except:
            self.logException()
        self.finish()
        
class WebHTTPChannel(http.HTTPChannel):
    def __init__(self, configuration, pluginRegistry, searchInterfaces, *args):
        self.configuration = configuration
        self.pluginRegistry = pluginRegistry
        self.searchInterfaces = searchInterfaces
        http.HTTPChannel.__init__(self, *args)
        
    def requestFactory(self, *args):
        return WebRequest(self.configuration, self.pluginRegistry, self.searchInterfaces, *args)
    
class QueryServerFactory(http.HTTPFactory):
    def __init__(self, configuration, pluginRegistry, searchInterfaces):
        self.configuration = configuration
        self.pluginRegistry = pluginRegistry
        self.searchInterfaces = searchInterfaces
        http.HTTPFactory.__init__(self)
        
    def protocol(self, *args):
        return WebHTTPChannel(self.configuration, self.pluginRegistry, self.searchInterfaces, *args)

def validateConfig(configuration):
    pass

def writepid(pidfile):
    f = open(pidfile, 'w')
    try:
        f.write(str(getpid()))
    finally:
        f.close()

def main(configfile):
    #TODO: add optparse
    configuration = config.read(configfile)
    validateConfig(configuration)
    
    pidfile = configuration.get('server.pidfile', None)
    if pidfile:
        writepid(pidfile)
    pluginRegistry = PluginRegistry(configuration)
    pluginRegistry.loadPlugins()
    
    constructorModule = configuration.get('search.interface.constructor')
    constructor = __import__(constructorModule)
    interfaceDictionary = constructor.construct(configuration)
    
    factory = QueryServerFactory(configuration, pluginRegistry, interfaceDictionary)
    port = int(configuration['server.port'])
    reactor.listenTCP(port, factory)
    log("Ready to rumble at port %s\n" % str(port))
    reactor.run()

if __name__ == '__main__':
    main(sys.argv[1])
