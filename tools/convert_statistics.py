#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

from sys import argv
from os.path import isfile

def convert_pickle_file(pickle_file):
    target = "%s.converted" % pickle_file
    if isfile(target):
        print "File '%s' already exists" % target
        return
        
    contents = open(pickle_file).read()
    converted = contents.replace('meresco.components.statistics', 'merescocore.components.statistics')
    
    fp = open(target, 'wb')
    try:
        fp.write(converted)
    finally:
        fp.close()
    return target

if __name__ == '__main__':
    args = argv[1:]
    if args == []:
        print "Usage: %s <pickle-file>" % argv[0]
        exit(1)

    if not isfile(args[0]):
        print "File '%s' not found" % args[0]
        exit(1)
    convert_pickle_file(args[0])