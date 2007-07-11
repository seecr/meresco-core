from os import getpid

def writepid(pidFile):
	if not pidFile:
		return
	
	f = open(pidFile, 'w')
	try:
		f.write(str(getpid()))
	finally:
		f.close()

