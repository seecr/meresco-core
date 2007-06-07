from meresco.queryserver.observers.oai.oaitool import OaiVerb
from meresco.queryserver.observers.stampcomponent import DATESTAMP, STAMP_PART
from xml.sax.saxutils import escape as xmlEscape

class OaiRecordVerb(OaiVerb):
	
	def writeRecord(self, webRequest, id, writeBody = True):
		isDeletedStr = self._isDeleted(id) and ' status="deleted"' or ''
		datestamp = str(getattr(self.xmlSteal(id, STAMP_PART), DATESTAMP))
		setSpecs = self._getSetSpecs(id)
		webRequest.write("""<record><header %s>
			<identifier>%s</identifier>
			<datestamp>%s</datestamp>
			%s
		</header>""" % (isDeletedStr, xmlEscape(id.encode('utf-8')), datestamp, setSpecs))
		if writeBody and not isDeletedStr:
			webRequest.write('<metadata>')
			self.all.write(webRequest, id, self._metadataPrefix)
			webRequest.write('</metadata>')
		webRequest.write('</record>')

	def _isDeleted(self, id):
		aTuple = self.any.isAvailable(id, "__tombstone__")
		ignored, hasTombstonePart = aTuple or (False, False)
		return hasTombstonePart
	
	def _getSetSpecs(self, id):
		aTuple = self.any.isAvailable(id, "__sets__")
		ignored, hasSetsPart = aTuple or (False, False)
		if hasSetsPart:
			sets = self.xmlSteal(id, "__sets__") 
			if hasattr(sets, 'set'):
				l = []
				for set in sets.set:
					l.append(set.setSpec)
				return "".join(map(lambda setSpec: "<setSpec>%s</setSpec>" % setSpec, l))
		return ""
