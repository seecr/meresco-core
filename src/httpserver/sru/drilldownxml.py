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

from xml.sax.saxutils import quoteattr, escape

class DrillDownXml:
	
	def __init__(self, core):
		self.core = core
		# i (kvs) this is exactly the point where we want to step away from our old philosophy of making everything an observer
	
	def writeExtraResponseData(self, webRequest):
		"""webRequest supports: write, and _arguments"""
		
		#questions:
		#<drilldown> - should reflect the original name?
		#x-meresco-drilldown ??
		#x-meresco-drilldown structure ??
		#shouldn't value really be called term??!
		
		webRequest.write("<drilldown>") #I think this should reflect the original name
		
		termsAndMaximums = webRequest._arguments.get('x-meresco-drilldown', [''])[0].split(",")
		asTuples = [tuple(s.split(":")) for s in termsAndMaximums]
		
		drillDownResults = self.core.process(asTuples)
		for fieldname, tuples in drillDownResults:
			webRequest.write('<field name=%s>' % quoteattr(fieldname))
			for value, count in tuples:
				webRequest.write('<value count=%s>%s</value>' % (quoteattr(str(count)), escape(str(value))))
			webRequest.write('</field>')
		
		webRequest.write("</drilldown>")
		
	def next(self):
		pass # I think a first step towards generators can be made here

