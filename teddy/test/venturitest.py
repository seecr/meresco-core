

from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace
from cq2utils.observable import Observable
from cq2utils.component import Notification
from cStringIO import StringIO
from amara import binderytools

from venturi import Venturi

class VenturiTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.storage = CallTrace('Storage')
		self.unit = CallTrace('Unit')
		self.storage.returnValues['getUnit'] = self.unit
		self.subject = Venturi('venturiName', self.storage)
		self.observer = CallTrace('Observer')
		self.observable = Observable()
		self.observable.addObserver(self.subject)
		self.subject.addObserver(self.observer)
		self.notification = Notification(method='add', id='id')
		
	def testWithNonExistingVenturiObject(self):
		meta = binderytools.bind_string('<meta><tagOne>data</tagOne></meta>').meta
		self.notification.partName = 'meta'
		self.notification.payload = meta
		
		self.observable.changed(self.notification)
		
		self.assertEquals(['getUnit'], [method.name for method in self.storage.calledMethods])
		self.assertEquals(['hasBox'], [method.name for method in self.unit.calledMethods])
		
		self.assertEquals(1, len(self.observer.calledMethods))
		method = self.observer.calledMethods[0]
		self.assertEquals('notify', method.name)
		self.assertEquals(1, len(method.arguments))
		notification = method.arguments[0]
		self.assertEquals('id', notification.id)
		self.assertEquals('add', notification.method)
		self.assertEquals('venturiName', notification.partName)
		self.assertEqualsWS("""<venturiName>
	<meta>
		<tagOne>data</tagOne>
	</meta>
</venturiName>""", notification.payload.xml())
		
	def testWithExistingVenturiObjectWithoutMeta(self):	
		meta = binderytools.bind_string('<meta><tagOne>data</tagOne></meta>').meta
		self.notification.partName = 'meta'
		self.notification.payload = meta
		
		self.unit.returnValues['hasBox'] = True
		self.unit.returnValues['openBox'] = StringIO("""<venturiName>
	<lom>
		<general><title>data</title></general>
	</lom>
</venturiName>""")
		
		self.observable.changed(self.notification)
		
		self.assertEquals(1, len(self.observer.calledMethods))
		notification = self.observer.calledMethods[0].arguments[0]
		self.assertEqualsWS("""<venturiName>
	<lom>
		<general><title>data</title></general>
	</lom>
	<meta>
		<tagOne>data</tagOne>
	</meta>
</venturiName>""", notification.payload.xml())
		
	def testWithExistingVenturiObjectWithMeta(self):	
		meta = binderytools.bind_string('<meta><tagOne>data</tagOne></meta>').meta
		self.notification.partName = 'meta'
		self.notification.payload = meta
		
		self.unit.returnValues['hasBox'] = True
		self.unit.returnValues['openBox'] = StringIO("""<venturiName>
	<meta>
		<already>here</already>
	</meta>
</venturiName>""")
		
		self.observable.changed(self.notification)
		
		self.assertEquals(1, len(self.observer.calledMethods))
		notification = self.observer.calledMethods[0].arguments[0]
		self.assertEqualsWS("""<venturiName>
	<meta>
		<tagOne>data</tagOne>
	</meta>
</venturiName>""", notification.payload.xml())
		