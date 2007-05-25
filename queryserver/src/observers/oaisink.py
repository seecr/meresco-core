## begin license ##
#
#    QueryServer is a framework for handling search queries.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of QueryServer.
#
#    QueryServer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    QueryServer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QueryServer; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from oai.oaitool import OaiVerb

class OaiSink(OaiVerb):
	
	def notify(self, webRequest):
		if webRequest.args.get('verb', []) == []:
			self.writeError(webRequest, 'badArgument', 'No "verb" argument found.')
		elif len(webRequest.args['verb']) > 1:
			self.writeError(webRequest, 'badArgument', 'More than one "verb" argument found.')
		else:
			 self.writeError(webRequest, 'badArgument', 'Argument value "%s" for verb illegal.' % webRequest.args['verb'][0])
		
	def undo(self, *args, **kwargs):
		"""Ignored"""
		pass
