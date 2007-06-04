from meresco.queryserver.observers.oai.oaitool import OaiVerb
from meresco.queryserver.observers.stampcomponent import DATESTAMP
from xml.sax.saxutils import escape as xmlEscape

class OaiRecordVerb(OaiVerb):
	
	def writeRecord(self, webRequest, id, writeBody = True):
		isDeletedStr = self._isDeleted(id) and ' status="deleted"' or ''
		datestamp = str(getattr(self.xmlSteal(id), DATESTAMP))
		webRequest.write("""<record><header %s>
			<identifier>%s</identifier>
			<datestamp>%s</datestamp>
		</header>""" % (isDeletedStr, xmlEscape(id.encode('utf-8')), datestamp))
		if writeBody and not isDeletedStr:
			webRequest.write('<metadata>')
			self.all.write(webRequest, id, self.partName)
			webRequest.write('</metadata>')
		webRequest.write('</record>')

	def _isDeleted(self, id):
		aTuple = self.any.isAvailable(id, "__tombstone__")
		ignored, hasTombstonePart = aTuple or (False, False)
		return hasTombstonePart