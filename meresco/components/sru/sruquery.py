## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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

from cqlparser import parseString, CQLParseException

class SRUQueryException(Exception):
    pass

class SRUQueryParameterException(SRUQueryException):
    pass

class SRUQueryParseException(SRUQueryException):
    pass

class SRUQuery:
    def __init__(self, arguments, defaultRecordSchema = "dc", defaultRecordPacking = "xml"):
        self.defaultRecordSchema = defaultRecordSchema
        self.defaultRecordPacking = defaultRecordPacking
        self._setupQuery(arguments)

    def _setupQuery(self, arguments):
        startRecord = arguments.get('startRecord', ['1'])[0]
        if not startRecord.isdigit() or int(startRecord) < 1:
            raise SRUQueryParameterException('startRecord')
        self.startRecord = int(startRecord)

        maximumRecords = arguments.get('maximumRecords', ['10'])[0]
        if not maximumRecords.isdigit() or int(maximumRecords) < 0:
            raise SRUQueryParameterException('maximumRecords')
        self.maximumRecords = int(maximumRecords)

        query = arguments.get('query', [''])[0]
        try:
            parseString(query)
        except CQLParseException, e:
            raise SRUQueryParseException(e)
        self.query = query
        
        sortKeys = arguments.get('sortKeys', [''])[0]
        self.sortBy, self.sortDirection = self._parseSort(sortKeys)
        
        self.recordSchema = arguments.get('recordSchema', [''])[0]
        if self.recordSchema == '':
            self.recordSchema = self.defaultRecordSchema
            
        self.x_recordSchema = filter(str.strip, arguments.get('x-recordSchema', []))
        
        self.recordPacking = arguments.get('recordPacking', [''])[0]
        if self.recordPacking == '':
            self.recordPacking = self.defaultRecordPacking
        
    def _parseSort(self, sortKeys):
        try:
            sortBy, ignored, sortDirection = sortKeys.split(',')
            return sortBy.strip(), bool(int(sortDirection))
        except ValueError:
            return None, None
