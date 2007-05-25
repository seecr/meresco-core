#!/bin/sh
## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

set -e

basedir=$(cd $(dirname $0); pwd)

source $basedir/functions.sh

isroot

echo "* 
* Now installing the CQ2 Search Appliance (Codenamed: Teddy)
[Press Enter to continue]"
read

TEDDY_HOME_DIR=$(cd $basedir/../..; pwd)
TEDDY_SITE_PACKAGES=$TEDDY_HOME_DIR/site-packages
GLOBAL_SITE_PACKAGES=/usr/lib/python2.4/site-packages

echo "*
* Installing required packages."

isDebian && PACKAGES="python2.4 python-profiler python2.4-xml python-twisted-web rsync wget gcj"
isSuSE && PACKAGES="python2.4 python-profiler python2.4-xml python-twisted-web rsync wget"
isFedora && PACKAGES="python PyXML python-twisted-web rsync wget"

$PM_INSTALL $PACKAGES
if [ -e /usr/bin/python2.4 ]; then
	rm /usr/bin/python
	ln -s /usr/bin/python2.4 /usr/bin/python
fi

if isDebian; then
	#check on right 4suite version
	if [ -d $GLOBAL_SITE_PACKAGES/Ft ]; then
		ftversion=$(python -c "import Ft; print Ft.__version__")
		if [ "$ftversion" != "1.0.2" ]; then
			aptitude remove python-4suite
		fi
	fi
	aptitude_install http://debian.cq2.org/ stable main python-amara1.1.7
fi

$basedir/install_daemontools.sh

echo "import sys
sys.setdefaultencoding('utf-8')
" > $GLOBAL_SITE_PACKAGES/sitecustomize.py


if isDebian; then
	echo "*
* Installing PyLucene for Teddy
*"
	if [ "$(uname -m)" == "x86_64" ]; then
		echo "!!! 64bit version not available !!!"
	else
		(
			directory=PyLucene-2.0.0
			filename=$directory.tar.gz
			cd /tmp
			if [ -d $directory ]; then 
				rm -rf $directory
			fi
			if [ ! -f $filename ]; then
				wget http://download.cq2.org/third-party/$filename
			fi
			tar xzf $filename
			cp -r $directory/python/* $GLOBAL_SITE_PACKAGES
			rm -rf $directory
		)
		
	fi
elif isFedora; then
	echo "*
* Installation of PyLucene 2.0 not supported for Fedora. You need
* to install it manually.
* See http://pylucene.osafoundation.org
[Press ENTER to continue.]"
	read
fi

if isDebian; then
	configureIpTables teddy 8000
else
	echo "* Please allow access to port 8000 on your firewall"
fi

echo "*
* Installation of Teddy finished.
*"

