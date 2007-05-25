#!/usr/bin/env python
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

import httplib
import sys

XML_DOCUMENT = """<otherXml>
with strings<nodes and="attributes"/>
</otherXml>"""

SRU_UPDATE_REQUEST = """<?xml version="1.0" encoding="UTF-8"?>
<updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="http://www.loc.gov/KVS_IHAVENOIDEA/">
	<srw:version>1.0</srw:version>
	<ucp:action>info:srw/action/1/%(action)s</ucp:action>
	<ucp:recordIdentifier>%(recordIdentifier)s</ucp:recordIdentifier>
	<srw:record>
		<srw:recordPacking>%(recordPacking)s</srw:recordPacking>
		<srw:recordSchema>%(recordSchema)s</srw:recordSchema>
		<srw:recordData>%(recordData)s</srw:recordData>
	</srw:record>	
</updateRequest>"""

def send(data, baseurl, port, path):
	connection = httplib.HTTPConnection(baseurl, port)
	connection.putrequest("POST", path)
	connection.putheader("Host", baseurl)
	connection.putheader("Content-Type", "text/xml; charset=\"utf-8\"")
	connection.putheader("Content-Length", str(len(data)))
	connection.endheaders()
	connection.send(data)
	
	response = connection.getresponse()
	print "STATUS:", response.status
	print "HEADERS:", response.getheaders()
	print "MESSAGE:", response.read()

if __name__ == "__main__":
	nrs = input("number of records (python code)> ")
	for i in nrs:
		send(SRU_UPDATE_REQUEST % {
			"action": "create",
			"recordIdentifier": "id_" + str(i),
			"recordPacking": "text/xml",
			"recordSchema": "rating",
			"recordData": XML_DOCUMENT}, 'localhost', 8000, '/darenet/sruRecordUpdate')