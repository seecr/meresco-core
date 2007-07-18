#!/bin/bash
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
source $basedir/functions.sh

if [ ! isDebian ] ; then
	echo Unsupported Linux Distribution. Only Debian is supported.
	exit
fi

INSTALL_DAEMONTOOLS="YES"
# Read options file if present
if [ ! -z "$INSTALL_OPTIONS_FILE" ]; then
    source $INSTALL_OPTIONS_FILE
fi

messageWithEnter "Now installing the Meresco Core"

message "Installing required packages."

PACKAGES="python2.4 python-profiler python-xml python-twisted-web rsync wget"

$PM_INSTALL $PACKAGES
if [ -e /usr/bin/python2.4 ]; then
	rm /usr/bin/python
	ln -s /usr/bin/python2.4 /usr/bin/python
fi

if [ "$INSTALL_DAEMONTOOLS" == "YES" ]; then
    $basedir/install_daemontools.sh
fi

echo "import sys
sys.setdefaultencoding('utf-8')
" > /usr/lib/python2.4/site-packages/sitecustomize.py

messageWithEnter "Installing prepackaged version of PyLucene."

aptitude install libc6 libgcc1 zlib1g libstdc++5
aptitude_install "http://debian.cq2.org" stable main pylucene python2.4-cq2utils python2.4-storage


testresult=/tmp/meresco.testresult
(
cd $merescodir/test
./alltests.py > $testresult 2>&1
)

if [ $? -eq 0 ] ; then
	message "Installation of MERESCO finished.

See the manual for further configuration steps.
"
    
else
	message "Installation of MERESO Core FAILED.
    
Result of the tests was:"
    cat $testresult
fi
rm $testresult
