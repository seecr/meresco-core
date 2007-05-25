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

from oai.oaitool import OaiVerb, DONE
from cq2utils.observable import Observable
from queryserver.observers.stampcomponent import TIME_FIELD

class OaiGetRecord(OaiVerb, Observable):
	"""4.1 GetRecord
Summary and Usage Notes

This verb is used to retrieve an individual metadata record from a repository. Required arguments specify the identifier of the item from which the record is requested and the format of the metadata that should be included in the record. Depending on the level at which a repository tracks deletions, a header with a "deleted" value for the status attribute may be returned, in case the metadata format specified by the metadataPrefix is no longer available from the repository or from the specified item.

Arguments

    * identifier a required argument that specifies the unique identifier of the item in the repository from which the record must be disseminated.
    * metadataPrefix a required argument that specifies the metadataPrefix of the format that should be included in the metadata part of the returned record . A record should only be returned if the format specified by the metadataPrefix can be disseminated from the item identified by the value of the identifier argument. The metadata formats supported by a repository and for a particular record can be retrieved using the ListMetadataFormats request.

Error and Exception Conditions

    * badArgument - The request includes illegal arguments or is missing required arguments.
    * cannotDisseminateFormat - The value of the metadataPrefix argument is not supported by the item identified by the value of the identifier argument.
    * idDoesNotExist - The value of the identifier argument is unknown or illegal in this repository.
"""
	def __init__(self):
		OaiVerb.__init__(self)
		Observable.__init__(self)
	
	def notify(self, webRequest):
		if webRequest.args.get('verb', None) != ['GetRecord']:
			return
		
		if self.isArgumentRepeated(webRequest):
			self.writeError(webRequest, 'badArgument', 'Argument "%s" may not be repeated.' % self.isArgumentRepeated(webRequest))
			return DONE

		actualArgs = set(webRequest.args.keys())
		expectedArgs = set(['verb', 'identifier', 'metadataPrefix'])
		tooMany = actualArgs.difference(expectedArgs)
		notEnough = expectedArgs.difference(actualArgs)
		
		if tooMany:
			self.writeError(webRequest, 'badArgument', 'Argument(s) %s is/are illegal.' % ", ".join(map(lambda s: '"%s"' %s, tooMany)))
			return DONE
		
		if notEnough:
			self.writeError(webRequest, 'badArgument', 'Missing argument(s) %s.' % ", ".join(map(lambda s: '"%s"' %s, notEnough)))
			return DONE
		
		id = webRequest.args['identifier'][0]
		partName = webRequest.args['metadataPrefix'][0]
		
		hasId, hasPartName = self.any.isAvailable(id, partName)
		
		if not hasId:
			self.writeError(webRequest, 'idDoesNotExist')
			return DONE
		
		if not hasPartName:
			self.writeError(webRequest, 'cannotDisseminateFormat')
			return DONE
		
		self.writeHeader(webRequest)
		self.writeRequestArgs(webRequest)
		webRequest.write('<GetRecord><record>')
		webRequest.write("""<header>
      <identifier>%s</identifier>
      <datestamp>%s</datestamp>
    </header>""" % (id, self.xmlSteal(id, TIME_FIELD)))

		webRequest.write('<metadata>')
		self.all.write(webRequest, id, partName)
		webRequest.write('</metadata>')
		
		webRequest.write('</record></GetRecord>')
		self.writeFooter(webRequest)
		return DONE
		
	
	def undo(self, *args, **kwargs):
		"""ignored"""
		pass
