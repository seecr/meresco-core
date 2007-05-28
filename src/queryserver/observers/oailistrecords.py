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

from oai.oaitool import OaiVerb, DONE, resumptionTokenFromString, ResumptionToken, ISO8601, ISO8601Exception
from cq2utils.observable import Observable
from meresco.queryserver.observers.stampcomponent import TIME_FIELD

from sys import getdefaultencoding
assert getdefaultencoding() == 'utf-8'

BATCH_SIZE = 200

class OaiListRecords(OaiVerb, Observable):
	"""4.5 ListRecords
Summary and Usage Notes

This verb is used to harvest records from a repository. Optional arguments permit selective harvesting of records based on set membership and/or datestamp. Depending on the repository's support for deletions, a returned header may have a status attribute of "deleted" if a record matching the arguments specified in the request has been deleted. No metadata will be present for records with deleted status.
Arguments

    * from an optional argument with a UTCdatetime value, which specifies a lower bound for datestamp-based selective harvesting.
    * until an optional argument with a UTCdatetime value, which specifies a upper bound for datestamp-based selective harvesting.
    * set an optional argument with a setSpec value , which specifies set criteria for selective harvesting.
    * resumptionToken an exclusive argument with a value that is the flow control token returned by a previous ListRecords request that issued an incomplete list.
    * metadataPrefix a required argument (unless the exclusive argument resumptionToken is used) that specifies the metadataPrefix of the format that should be included in the metadata part of the returned records. Records should be included only for items from which the metadata format
      matching the metadataPrefix can be disseminated. The metadata formats supported by a repository and for a particular item can be retrieved using the ListMetadataFormats request.

Error and Exception Conditions

    * badArgument - The request includes illegal arguments or is missing required arguments.
    * badResumptionToken - The value of the resumptionToken argument is invalid or expired.
    * cannotDisseminateFormat - The value of the metadataPrefix argument is not supported by the repository.
    * noRecordsMatch - The combination of the values of the from, until, set and metadataPrefix arguments results in an empty list.
    * noSetHierarchy - The repository does not support sets.
"""
	def __init__(self):
		OaiVerb.__init__(self)
		Observable.__init__(self)
	
	def notify(self, webRequest):
		#TODO in het algemeen moet er nog wat gebeuren met fouten die uit 'ons' binnenste komen. Specifiek wordt er nog slecht omgegegaan met
		#verrotte resumptionTokens
		#metadataPrefixen die niet voorkomen
		
		if webRequest.args.get('verb', None) != ['ListRecords']:
			return
		
		if self.isArgumentRepeated(webRequest):
			return self.writeError(webRequest, 'badArgument', 'Argument "%s" may not be repeated.' % self.isArgumentRepeated(webRequest))
		
		if set(webRequest.args.keys()) == set(['verb', 'resumptionToken']):
			token = resumptionTokenFromString(webRequest.args['resumptionToken'][0])
			partName = token._metadataPrefix
			queryResult = self.any.listRecords(token._continueAt)
			return self.writeMessage(webRequest, partName, queryResult, True)
		
		if webRequest.args.get('resumptionToken', None):
			return self.writeError(webRequest, 'badArgument', '"resumptionToken" argument may only be used exclusively.')
		
		if not webRequest.args.get('metadataPrefix', None):
			return self.writeError(webRequest, 'badArgument', 'Missing argument "resumptionToken" or "metadataPrefix"')
		
		tooMuch = set(webRequest.args.keys()).difference(['verb', 'metadataPrefix', 'from', 'until', 'set'])
		if tooMuch:
			return self.writeError(webRequest, 'badArgument', 'Argument(s) %s is/are illegal.' % ", ".join(map(lambda s: '"%s"' %s, tooMuch)))
		
		partName = webRequest.args['metadataPrefix'][0]
		try:
			oaiFrom = webRequest.args.get('from', [None])[0]
			oaiFrom = oaiFrom and ISO8601(oaiFrom)
			oaiUntil = webRequest.args.get('until', [None])[0]
			oaiUntil = oaiUntil and ISO8601(oaiUntil)
			if oaiFrom and oaiUntil:
				if oaiFrom.isShort() != oaiUntil.isShort():
					return self.writeError(webRequest, 'badArgument', 'from and/or until arguments must match in length')
				if str(oaiFrom) > str(oaiUntil):
					return self.writeError(webRequest, 'badArgument', 'from argument must be smaller than until argument')
			oaiFrom = oaiFrom and oaiFrom.floor()
			oaiUntil = oaiUntil and oaiUntil.ceil()
		except ISO8601Exception, e:
			return self.writeError(webRequest, 'badArgument', 'from and/or until arguments are faulty')
		queryResult = self.any.listRecords(oaiFrom = oaiFrom, oaiUntil = oaiUntil)
		return self.writeMessage(webRequest, partName, queryResult)
		
	def writeMessage(self, webRequest, partName, queryResult, writeCloseToken = False):
		self.writeHeader(webRequest)
		self.writeRequestArgs(webRequest)
		webRequest.write('<ListRecords>')
		j = -1
		for i, id in enumerate(queryResult):
			if i == BATCH_SIZE:
				continueAt = self.xmlSteal(prevId, 'unique')
				resumptionToken = ResumptionToken(partName, continueAt)
				webRequest.write('<resumptionToken>%s</resumptionToken>' % str(resumptionToken))
				writeCloseToken = False
				break
			
			aTuple = self.any.isAvailable(id, "__tombstone__")
			ignored, hasTombstonePart = aTuple or (False, False)
			isDeleted = hasTombstonePart and ' status="deleted"' or ''
			
			webRequest.write("""<record><header %s>
				<identifier>%s</identifier>
				<datestamp>%s</datestamp>
			</header>""" % (isDeleted, id.encode('utf-8'), self.xmlSteal(id, TIME_FIELD).upper())) #TODO remove UPPERCASEHACK
			
			if not isDeleted:
				webRequest.write('<metadata>')
				self.all.write(webRequest, id, partName)
				webRequest.write('</metadata>')
			webRequest.write('</record>')
			prevId = id
			j = i
		if writeCloseToken and j <= BATCH_SIZE:
			webRequest.write('<resumptionToken/>')
		webRequest.write('</ListRecords>')
		self.writeFooter(webRequest)
		return DONE

	def undo(self, *args, **kwargs):
		"""ignored"""
		pass
