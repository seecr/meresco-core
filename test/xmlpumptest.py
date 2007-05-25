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

from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.observable import Observable
from cq2utils.component import Notification
from cq2utils.calltrace import CallTrace
from amara import binderytools

from xmlpump import XmlInflate, XmlDeflate

class XmlPumpTest(CQ2TestCase):
	def testInflate(self):
		observer = CallTrace('Observer')
		observable = Observable()
		subject = XmlInflate()
		observable.addObserver(subject)
		subject.addObserver(observer)
		
		notification = Notification('method', 'id', 'partName')
		notification.payload = """<tag><content>contents</content></tag>"""
		
		observable.changed(notification)
		
		self.assertEquals(['notify'], [m.name for m in observer.calledMethods])
		newNotification = observer.calledMethods[0].arguments[0]
		self.assertNotEqual(id(notification), id(newNotification))
		
		self.assertEquals(notification.payload, newNotification.payload.xml())
		self.assertEquals('tag', newNotification.payload.localName)
		self.assertEquals('content', newNotification.payload.content.localName)
		
		
	
	def testDeflate(self):
		observer = CallTrace('Observer')
		observable = Observable()
		subject = XmlDeflate()
		observable.addObserver(subject)
		subject.addObserver(observer)
		
		notification = Notification('method', 'id', 'partName')
		notification.payload = binderytools.bind_string("""<tag><content>contents</content></tag>""").tag
		
		observable.changed(notification)
		
		self.assertEquals(['notify'], [m.name for m in observer.calledMethods])
		newNotification = observer.calledMethods[0].arguments[0]
		self.assertNotEqual(id(notification), id(newNotification))
		
		self.assertEquals(notification.payload.xml(), newNotification.payload)
		
		
	def testJoin(self):
		observer = CallTrace('Observer')
		observable = Observable()
		subject1 = XmlInflate()
		subject2 = XmlDeflate()
		observable.addObserver(subject1)
		subject1.addObserver(subject2)
		subject2.addObserver(observer)
		
		notification = Notification('method', 'id', 'partName')
		notification.payload = """<tag><content>contents</content></tag>"""
		
		observable.changed(notification)
		
		self.assertEquals(['notify'], [m.name for m in observer.calledMethods])
		newNotification = observer.calledMethods[0].arguments[0]
		self.assertNotEqual(id(notification), id(newNotification))
		self.assertEquals(notification.payload, newNotification.payload)
