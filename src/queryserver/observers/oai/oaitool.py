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

from time import gmtime, strftime
from xml.sax.saxutils import escape as xmlEscape
from xml.utils import iso8601

DONE = 1

class OaiVerb(object):
	
	def __init__(self, supportedVerbs, argsDef):
		self._supportedVerbs = supportedVerbs
		self._argsDef = argsDef
	
	def notify(self, webRequest):
		self._verb = webRequest.args.get('verb', [None])[0]
		if not self._verb in self._supportedVerbs:
			return
		
		error = self._doElementaryArgumentsValidation(webRequest)
		if error:
			return self.writeError(webRequest, 'badArgument', error)
		
		error = self.preProcess(webRequest)
		if error:
			return error
		
		self.writeHeader(webRequest)
		self.writeRequestArgs(webRequest)
		
		webRequest.write('<%s>' % self._verb)
		self.process(webRequest)
		webRequest.write('</%s>' % self._verb)
		
		self.writeFooter(webRequest)
		return DONE
	
	def preProcess(self, webRequest):
		"""Hook"""
		pass
	
	def process(self, webRequest):
		"""Hook"""
		pass
			
	def getTime(self):
		return strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
	
	def getRequestUrl(self, webRequest):
		return 'http://%s:%s' % (webRequest.getRequestHostname(), webRequest.getHost().port) + webRequest.path
	
	def writeHeader(self, webRequest):
		webRequest.setHeader('content-type', 'text/xml; charset=utf-8')
		webRequest.write(OAIHEADER)
		webRequest.write(RESPONSE_DATE % self.getTime())
		
	def writeRequestArgs(self, webRequest):
		url = self.getRequestUrl(webRequest)
		args = ' '.join(['%s="%s"' % (xmlEscape(k), xmlEscape(v[0])) for k,v in sorted(webRequest.args.items())])
		webRequest.write(REQUEST % locals())
	
	def writeError(self, webRequest, statusCode, addionalMessage = '', echoArgs = True):
		space = addionalMessage and ' ' or '' 
		message = ERROR_CODES[statusCode] + space + addionalMessage
		self.writeHeader(webRequest)
		url = self.getRequestUrl(webRequest)
		if statusCode in ["badArgument", "badResumptionToken", "badVerb"]:
			"""in these cases it is illegal to echo the arguments back; since the arguments are not valid in the first place the responce will not validate either"""
			args = ''
			webRequest.write(REQUEST % locals())
		else:
			self.writeRequestArgs(webRequest)
		webRequest.write(ERROR % locals())
		self.writeFooter(webRequest)
		return DONE
		
	def xmlSteal(self, id, partName):
		from StringIO import StringIO
		from amara.binderytools import bind_string
		buffer = StringIO()
		self.all.write(buffer, id, partName)
		return bind_string(buffer.getvalue()).childNodes[0]
		
	def writeFooter(self, webRequest):
		webRequest.write(OAIFOOTER)
		
	def _isArgumentRepeated(self, webRequest):
		for k, v in webRequest.args.items():
			if len(v) > 1:
				return k
		return False
		
	def _select(self, neededNess):
		result = []
		for arg, definition in self._argsDef.items():
			if definition == neededNess:
				result.append(arg)
		return result
	
	def ___set(self, key, value):
		setattr(self, "_" + key, value[0])
	
	def _doElementaryArgumentsValidation(self, webRequest):
		if self._isArgumentRepeated(webRequest):
			return 'Argument "%s" may not be repeated.' % self._isArgumentRepeated(webRequest)
		
		exclusiveArguments = self._select('exclusive')
		for exclusiveArgument in exclusiveArguments:
			if exclusiveArgument in webRequest.args.keys():
				if set(webRequest.args.keys()) != set(['verb', exclusiveArgument]):
					return '"%s" argument may only be used exclusively.' % exclusiveArgument
				self.___set(exclusiveArgument, webRequest.args[exclusiveArgument])
				return
			else:
				self.___set(exclusiveArgument, [None])
			
		missing = []
		for requiredArgument in self._select('required'):
			if not requiredArgument in webRequest.args.keys():
				missing.append(requiredArgument)
			self.___set(requiredArgument, webRequest.args.get(requiredArgument, [None]))
		quote = lambda l: (map(lambda s: '"%s"' % s, l))
		if missing:
			return 'Missing argument(s) ' + \
				" or ".join(quote(exclusiveArguments) + \
				[" and ".join(quote(missing))]) + "."
			
		for optionalArgument in self._select('optional'):
			self.___set(optionalArgument, webRequest.args.get(optionalArgument, [None]))
		
		tooMuch = set(webRequest.args.keys()).difference(self._argsDef.keys() + ['verb'])
		if tooMuch:
			return 'Argument(s) %s is/are illegal.' % ", ".join(map(lambda s: '"%s"' %s, tooMuch))
		

def resumptionTokenFromString(s):
	result = ResumptionToken()
	result.loadString(s)
	return result

class ResumptionToken:
	
	SHORT = {
		'm': '_metadataPrefix',
		'c': '_continueAt',
		'f': '_from',
		'u': '_until',
		's': '_set'}
	
	def __init__(self,
		_metadataPrefix = '',
		_continueAt = '0',
		_from = '',
		_until = '',
		_set = ''):
		self._metadataPrefix = _metadataPrefix
		self._continueAt = _continueAt
		self._from = _from or '' #blank out "None"
		self._until = _until or ''
		self._set = _set
	
	def __str__(self):
		short = ResumptionToken.SHORT
		return ';'.join(map(lambda k: "%s=%s" %(k, self.__dict__[short[k]]), short.keys()))
	
	def __eq__(self, other):
		return \
			ResumptionToken == other.__class__ and \
			self._metadataPrefix == other._metadataPrefix and \
			self._continueAt == other._continueAt and \
			self._from == other._from and \
			self._until == other._until and \
			self._set == other._set
			
	def loadString(self, s):
		lines = s.split(';')
		lines = map(lambda s: s.split('='), lines)
		for elem in lines:
			if len(elem) == 2:
				k, v = elem
				if k in ResumptionToken.SHORT:
					#this is a possible location for validity check of v
					setattr(self, ResumptionToken.SHORT[k], v)
					
class ISO8601Exception(Exception):
	pass

class ISO8601:
	short, long = [len('YYYY-MM-DD'), len('YYYY-MM-DDThh:mm:ssZ')]
	
	def __init__(self, s):
		if not len(s) in [self.short, self.long]:
			raise ISO8601Exception(s)
		try:
			iso8601.parse(s)
		except ValueError, e:
			raise ISO8601Exception(s)
		self.s = s
	
	def _extend(self, extension):
		if not self.isShort():
			return self.s
		return self.s + extension
	
	def floor(self):
		return self._extend("T00:00:00Z")
	
	def ceil(self):
		return self._extend("T23:59:59Z")
	
	def __str__(self):
		return self.floor()
	
	def isShort(self):
		return len(self.s) == self.short

OAIHEADER = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
"""

RESPONSE_DATE = """<responseDate>%s</responseDate>"""

REQUEST = """<request %(args)s>%(url)s</request>"""

OAIFOOTER = """</OAI-PMH>"""

ERROR = """<error code="%(statusCode)s">%(message)s</error>"""

# http://www.openarchives.org/OAI/openarchivesprotocol.html#ErrorConditions
ERROR_CODES = {
	'badArgument': 'The request includes illegal arguments, is missing required arguments, includes a repeated argument, or values for arguments have an illegal syntax.',
	'badResumptionToken': 'The value of the resumptionToken argument is invalid or expired.',
	'badVerb': 'Value of the verb argument is not a legal OAI-PMH verb, the verb argument is missing, or the verb argument is repeated.',
	'cannotDisseminateFormat': 'The metadata format identified by the value given for the metadataPrefix argument is not supported by the item or by the repository.',
	'idDoesNotExist': 'The value of the identifier argument is unknown or illegal in this repository.',
	'noRecordsMatch': 'The combination of the values of the from, until, set and metadataPrefix arguments results in an empty list.',
	'noMetadataFormats': 'There are no metadata formats available for the specified item.',
	'noSetHierarchy': 'The repository does not support sets.'
}
