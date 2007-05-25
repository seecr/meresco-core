#!/usr/bin/env python

from PyLucene import FSDirectory, IndexReader

def unlock(path):
	"""
	Unlock the directory specified by path.
	This is a manual operation, when locking somehow has gone wrong.
	"""
	IndexReader.unlock(FSDirectory.getDirectory(path, False))