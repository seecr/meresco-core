# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2010 Stichting Kennisnet http://www.kennisnet.nl
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
from meresco.core import Observable
from weightless import HttpServer
from cgi import parse_qs
from urlparse import urlsplit
from StringIO import StringIO
from socket import gethostname
from utils import serverUnavailableHtml

class ObservableHttpServer(Observable):
    def __init__(self, reactor, port, timeout=1, prio=None, sok=None, maxConnections=None):
        Observable.__init__(self)
        self._port = port
        self._reactor = reactor
        self._timeout = timeout
        self._started = False
        self._prio = prio
        self._sok = sok
        self._maxConnections = maxConnections

    def startServer(self):
        """Starts server,

        When running a http server on port 80, this method should be called by the
        root user. In other cases it will be started when initializing all observers,
        see observer_init()
        """
        self._keepHttpServerForTestingSupport = \
            HttpServer(self._reactor, self._port, self._connect,
                timeout=self._timeout, prio=self._prio, sok=self._sok,
                maxConnections=self._maxConnections,
                errorHandler=self._error)
        self._started = True

    def observer_init(self):
        if not self._started:
            self.startServer()

    def _connect(self, **kwargs):
        return self.handleRequest(port=self._port, **kwargs)

    def _error(self, **kwargs):
        yield serverUnavailableHtml +\
        '<html><head></head><body><h1>Service Unavailable</h1></body></html>'
        self.do.logHttpError(**kwargs)

    def handleRequest(self, RequestURI=None, *args, **kwargs):
        scheme, netloc, path, query, fragments = urlsplit(RequestURI)
        arguments = parse_qs(query, keep_blank_values=True)
        requestArguments = {
            'scheme': scheme, 'netloc': netloc, 'path': path, 'query': query, 'fragments': fragments,
            'arguments': arguments,
            'RequestURI': RequestURI}
        requestArguments.update(kwargs)
        return self.all.handleRequest(**requestArguments)

