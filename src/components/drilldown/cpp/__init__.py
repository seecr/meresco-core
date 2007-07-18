## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
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
