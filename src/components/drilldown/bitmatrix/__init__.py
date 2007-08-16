from os import system
from os.path import abspath, dirname

if '/trunk/' in abspath(__file__):
	system("cd %s; python setup.py build_ext --inplace" % dirname(__file__))

from bitmatrix import BitMatrix

