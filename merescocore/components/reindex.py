## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
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

from merescocore.framework import Observable
from lxml.etree import parse
from StringIO import StringIO

EMPTYDOC = parse(StringIO('<empty/>'))

class Reindex(Observable):
    def __init__(self, partName):
        Observable.__init__(self)
        self._partName = partName

    def reindex(self, partialIdentifier=''):
        for identifier in self.any.listIdentifiers(self._partName, partialIdentifier=partialIdentifier):
            try:
                self.do.add(identifier, 'ignoredName', EMPTYDOC)
            except:
                print 'ERROR', identifier
                raise
            yield identifier

class ReindexConsole(Observable):
    def handleRequest(self, *args, **kwargs):
        arguments = kwargs.get('arguments', {})
        partialIdentifier=arguments.get('partialIdentifier', [''])[0]
        yield "HTTP/1.0 200 OK\r\nContent-Type: plain/text\r\n\r\n"
        for id in self.all.reindex(partialIdentifier=partialIdentifier):
            yield id + "\n"
        yield "done"
