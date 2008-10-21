#!/usr/bin/env python
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

from PyLucene import IndexReader, Term
from sys import argv
from os.path import basename

def findFields(reader):
    return reader.getFieldNames(IndexReader.FieldOption.ALL)

def printFields(fields):
    for field in sorted(fields):
        print field

def listTerms(reader, fields):
    termDocs = reader.termDocs()
    for field in sorted(fields):
        print field
        termEnum = reader.terms(Term(field, ''))
        while True:
            if termEnum.term().field() != field:
                break
            termDocs.seek(termEnum)
            docIds = []
            while termDocs.next():
                docIds.append(termDocs.doc())
            print termEnum.term().text(), len(docIds)
            if not termEnum.next():
                break
        print '\n'

if __name__ == '__main__':
    args = argv[1:]
    if len(args) < 1:
        print 'Usage: %s <index directory name> --fields | --terms' % basename(argv[0])    
    else:
        index = args[0]
        reader = IndexReader.open(index)
        fields = findFields(reader)
        if '--fields' in args:
            printFields(fields)
        elif '--terms' in args:
            listTerms(reader, fields)

