## begin license ##
#
#    LOREnet is a tool for sharing knowledge within and beyond the walls of 
#    your own school or university.
#    Copyright (C) 2006-2007 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of LOREnet.
#
#    LOREnet is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    LOREnet is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with LOREnet; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from unittest import TestCase
from ieeelomvalidatecomponent import IeeeLomValidateComponent
from cq2utils.component import Notification

class ValidateComponentTest(TestCase):
	def testOne(self):
		component = IeeeLomValidateComponent()
		class Interceptor:
			def notify(inner, *args):
				self.args = args
			def undo(inner, *args): pass
		interceptor = Interceptor()
		component.addObserver(interceptor)
		notification = Notification()
		notification.payload = '<lom xmlns="http://ltsc.ieee.org/xsd/LOM"/>'
		component.notify(notification)
		self.assertEquals((notification,), self.args)
