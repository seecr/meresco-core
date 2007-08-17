from os import system
from os.path import abspath, dirname

if 'trunk/' in abspath(__file__):
	status = system("cd %s; python setup.py build_ext --inplace" % dirname(__file__))
	print status
	if status:
		raise ImportError()

from bitmatrix import BitMatrix

