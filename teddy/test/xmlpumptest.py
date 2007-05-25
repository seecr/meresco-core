
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