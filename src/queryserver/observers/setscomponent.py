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

from cq2utils.observable import Observable
from cq2utils.component import Notification
from amara.binderytools import bind_string

SETS_PART = "__sets__"

class SetsComponent(Observable):
	
	def notify(self, notification):
		setsNotification = Notification("add", notification.id, SETS_PART, bind_string(self.xml(notification.sets)))
		self.changed(setsNotification)
	
	def xml(self, sets):
		return """<%s>%s</%s>""" % (SETS_PART, "".join(map(lambda x: """<set><setSpec>%s</setSpec><setName>%s</setName></set>""" % x, sets)), SETS_PART)

	def undo(self, *args, **kwargs):
		pass
