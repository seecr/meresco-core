def _init():
	from os import system, stat
	from stat import ST_MTIME
	from os.path import abspath, join, isfile
	
	if len(__path__) != 1:
		raise Exception("__path__ contains multiple paths, this is not supported yet")
	
	mypath =  abspath(__path__[0])
	
	statWithExists = lambda filename: isfile(join(mypath, filename)) and stat(join(mypath, filename))[ST_MTIME] or -1
	
	myStat = lambda filename: stat(join(mypath, filename))[ST_MTIME]
	
	modtimeH = myStat('BitArray.h')
	modtimeCPP = myStat('BitArray.cpp')
	modtimeSO = statWithExists('_bitarray.so')
	
	if modtimeH > modtimeSO or modtimeCPP > modtimeSO:
		system("cd %s; ./make_so.sh" % mypath)
		if myStat('_bitarray.so') == modtimeSO:
			raise Exception("Compile process failed")
	
_init()
del _init