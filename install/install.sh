#!/bin/sh
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

set -e

basedir=$(cd $(dirname $0); pwd)
merescodir=$(cd $basedir/..; pwd)
teddydir=$merescodir/teddy
distdir=$merescodir/dist
cq2_dep_dir=$merescodir/lib

source $basedir/functions.sh

test -d $cq2_dep_dir || mkdir $cq2_dep_dir
$basedir/install_dist.sh $cq2_dep_dir cq2utils 4.1
$basedir/install_dist.sh $cq2_dep_dir storage 3.2
$basedir/install_dist.sh $cq2_dep_dir cqlparser 1.2



echo "* 
* Now installing the Meresco Search Component
[Press Enter to continue]"
read

echo "*
* Installing required packages."

isDebian && PACKAGES="python2.4 python-profiler python-xml python-twisted-web rsync wget"
isSuSE && PACKAGES="python2.4 python-profiler python2.4-xml python-twisted-web rsync wget"
isFedora && PACKAGES="python PyXML python-twisted-web rsync wget gcc"

$PM_INSTALL $PACKAGES
if [ -e /usr/bin/python2.4 ]; then
	rm /usr/bin/python
	ln -s /usr/bin/python2.4 /usr/bin/python
fi

$basedir/install_daemontools.sh

echo "import sys
sys.setdefaultencoding('utf-8')
" > /usr/lib/python2.4/site-packages/sitecustomize.py

if isDebian; then
	echo "*
* Installing PyLucene for Teddy
*
* Installing prepackaged version of PyLucene, available only to i386 processor.
[Press Enter to continue]"
	read
	aptitude install libc6 libgcc1 zlib1g libstdc++5
	dpkg -i $distdir/libgcj-common_1%3a4.1.1-21_i386.deb
	dpkg -i $distdir/libgcj5_3.4.3-13sarge1_i386.deb
	dpkg -i $distdir/python2.4-pylucene_1.9.1-1_i386.deb

elif isFedora; then
	# PyLucene must be compiled with gcc/gcj 3.4.6 to avoid run time crashes
	# Download it from CQ2 server, configure and compile it.
	if [ ! -f /usr/local/bin/gcj ]; then
		echo "* Installing GCC and GCJ 3.4.6"
		(cd /tmp
		rm -f gcc-3.4.6.tar.bz2
		wget http://download.cq2.org/third-party/gcc-3.4.6.tar.bz2
		tar xjf gcc-3.4.6.tar.bz2
		cd gcc-3.4.6
		./configure
		make
		make install)
	fi
	
	# We *NEED* swig 1.3.23 or 1.3.24, any other version of swig will not work.
	# Download swig from the CQ2 server, unpack it, run configure and compile.
	if [ ! -f /usr/local/bin/swig ]; then
		echo "* Installing SWIG 1.3.24"
		(cd /tmp
		rm -f swig-1.3.24.tar.gz
		wget http://download.cq2.org/third-party/swig-1.3.24.tar.gz
		tar -xzf swig-1.3.24.tar.gz
		cd SWIG-1.3.24
		./configure
		make
		make install)
	fi

	# Install PyLucene from source. Add the configuration settings to the
	# makefile and compile.
	if [ ! -f /usr/lib/python2.4/site-packages/PyLucene.py ]; then
		echo "* Installing PyLucene 1.9.1"
		(cd /tmp
		rm -rf PyLucene-src*
		wget http://download.cq2.org/third-party/PyLucene-src-1.9.1.tar.gz
		tar -xzf PyLucene-src-1.9.1.tar.gz
		yum install gcc-java gcc-c++ python-devel
		cd PyLucene-src-1.9.1
		cp Makefile Makefile.orig
		cat << EOF > Makefile
PREFIX=/usr
PREFIX_PYTHON=\$(PREFIX)
SWIG=\$(PREFIX)/local/bin/swig
GCJ_HOME=/usr/local
GCJ_VER=3
EOF
		cat Makefile.orig >> Makefile
		make
		make install
		)
	fi
fi

username=teddy
groupname=$(id --group --name $username)
configfile=$teddydir/config/config.xml
if [ ! -f $configfile ]; then
	echo "<?xml version=\"1.0\"?>
<configuration>
        <storage>$merescodir/index/storage</storage>
        <lucene>$merescodir/index/lucene</lucene>
</configuration>" > $configfile
	chown $username.$groupname $configfile
fi

#unpack example index
(
	cd $merescodir
	tar xzf $distdir/example_index.tar.gz
	chown $username.$groupname index -R
)

servicedir=/service/teddy-service
if [ ! -d $servicedir ]; then
	mkdir -p $servicedir/log/main
	chown $username.$groupname $servicedir/log/main
	echo "#!/bin/bash

exec /usr/local/bin/setuidgid $username /usr/local/bin/multilog t -n20 $servicedir/log/main 2>&1" > $servicedir/log/run
	chmod +x $servicedir/log/run

	echo "#!/bin/bash

cd $teddydir/src
export PYTHONPATH=$merescodir:$cq2_dep_dir:$teddydir/amara1.0
export LD_LIBRARY_PATH=/usr/local/lib
export TEDDY_CONFIG_PATH=$teddydir/config
exec /usr/local/bin/setuidgid $username python2.4 teddyserver.py 2>&1" > $servicedir/run
	chmod +x $servicedir/run
fi

if isDebian; then
	configureIpTables teddy 8000
else
	echo "* Please allow access to port 8000 on your firewall"
fi

echo "*
* Installation of Teddy finished.
*
* We have created an example index in order to test the installation.
* - Go to http://localhost:8000/sru?version=1.1&operation=searchRetrieve&query=year:2007
* 
* See the manual for further configuration steps.
*"

