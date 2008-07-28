#!/usr/bin/env python

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
        while termEnum.next():
            termDocs.seek(termEnum)
            docIds = []
            while termDocs.next():
                docIds.append(termDocs.doc())
            print termEnum.term().text(), len(docIds)
            if termEnum.term().field() != field:
                break
        print '\n'

if __name__ == '__main__':
    args = argv[1:]
    index = 'index'
    reader = IndexReader.open(index)
    fields = findFields(reader)
    if '--fields' in args:
        printFields(fields)
    elif '--terms' in args:
        listTerms(reader, fields)
    else:
        print 'Usage: %s --fields | --terms' % basename(argv[0])
