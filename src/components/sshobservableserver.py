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

from cq2utils.networking.growlserver import GrowlServer
from cq2utils.component import Notification
from cStringIO import StringIO
from amara.bindery import is_element
from meresco.framework.observable import Observable

class TeddyGrowlServer(GrowlServer, Observable):
    def __init__(self, aReadWriteStream, *args):
        GrowlServer.__init__(self, aReadWriteStream)
        Observable.__init__(self)

    def _processDocument(self, aDocument):
        id = str(aDocument.id)

        if hasattr(aDocument, "delete") and aDocument.delete == 'true':
            self.do.delete(id) #yield?
            return

        for part in aDocument.part:
            payload = StringIO()
            if part.type == 'text/plain':
                payload.write(str(part))
            elif part.type == 'text/xml':
                for child in filter(is_element, part.childNodes):
                    payload.write(child.xml())
            else:
                pass #i.e. just not stored KVS: vraagteken - is dit geen probleem?

            self.do.add(id, part.name, payload.getvalue()) #yield?
