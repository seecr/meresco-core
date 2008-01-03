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

from cq2utils.cq2testcase import CQ2TestCase

from cq2utils.calltrace import CallTrace
from meresco.framework.observable import Observable
from cStringIO import StringIO

class ObservableTestCase(CQ2TestCase):
    
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.observable = Observable()
        self.subject = self.getSubject()
        self.observable.addObserver(self.subject)
        self.request = CallTrace('Request')
        host = CallTrace('Host')
        host.port = 8000
        self.request.returnValues['getRequestHostname'] = 'localhost'
        self.request.returnValues['getHost'] = host
        self.stream = StringIO()
        self.request.write = self.stream.write
