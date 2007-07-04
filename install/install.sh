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

if [ ! isDebian ] ; then
	echo Unsupported Linux Distribution. Only Debian is supported.
	exit
fi


basedir=$(cd $(dirname $0); pwd)
merescodir=$(cd $basedir/..; pwd)
teddydir=$merescodir/teddy
distdir=$merescodir/dist
cq2_dep_dir=$merescodir/lib

source $basedir/functions.sh

test -d $cq2_dep_dir || mkdir $cq2_dep_dir
$basedir/install_dist.sh $cq2_dep_dir cq2utils 4.2
$basedir/install_dist.sh $cq2_dep_dir storage 3.2
$basedir/install_dist.sh $cq2_dep_dir cqlparser 1.2

echo "* 
* Now installing the Meresco Core
[Press Enter to continue]"
read

echo "*
* Installing required packages."

PACKAGES="python2.4 python-profiler python-xml python-twisted-web rsync wget"

$PM_INSTALL $PACKAGES
if [ -e /usr/bin/python2.4 ]; then
	rm /usr/bin/python
	ln -s /usr/bin/python2.4 /usr/bin/python
fi

$basedir/install_daemontools.sh

echo "import sys
sys.setdefaultencoding('utf-8')
" > /usr/lib/python2.4/site-packages/sitecustomize.py

echo "*
* Installing prepackaged version of PyLucene.
[Press Enter to continue]"
read

aptitude install libc6 libgcc1 zlib1g libstdc++5
aptitude_install "http://debian.cq2.org" stable main pylucene

PYLUCENEVERSION=`python -c "import PyLucene; print PyLucene.VERSION"`
if [ "$PYLUCENEVERSION" == "2.0.0" ] ; then
	echo "* 
* Installation of MERESCO finished.
*
* See the manual for further configuration steps.
"
else
	echo "*
* Installation of MERESO Core FAILED.
* Tried 'import PyLucene; print PyLucene.VERSION == 2.0.0', but result was
* $PYLUCENEVERSION
"
fi

