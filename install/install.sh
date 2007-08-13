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

PACKAGES="python2.4 python-profiler python-xml python-twisted-web rsync wget python-lxml bzip2"

$PM_INSTALL $PACKAGES
if [ -e /usr/bin/python2.4 ]; then
    rm /usr/bin/python
    ( cd /usr/bin; ln -s python2.4 python)
fi

if [ "$INSTALL_DAEMONTOOLS" == "YES" ]; then
    $basedir/install_daemontools.sh
fi

echo "import sys
sys.setdefaultencoding('utf-8')
" > /usr/lib/python2.4/site-packages/sitecustomize.py

depsdir=$merescodir/deps.d
tempdir=$merescodir/temp
distdir=$merescodir/dist
messageWithEnter "Installing prepackaged version of PyLucene."
aptitude install libc6 libgcc1 zlib1g libstdc++5 python2.4-dev swig

architecture=$(dpkg --print-architecture)
luceneverion=2.0.0
lucenename=pylucene-${luceneverion}-$architecture
lucenedir=$depsdir/$lucenename
if [ ! -d $lucenedir ]; then
    securitydir=/usr/lib/python2.4/site-packages/security
    test -d $securitydir || mkdir $securitydir
    if [ "$architecture" == "amd64" ]; then
        (
            cd $depsdir
            tar xjf $distdir/$lucenename.tar.bz2
            tar xjf $distdir/libgcj5.tar.bz2
            cp $lucenedir/security/*.security $securitydir
        )
    elif [ "$architecture" == "i386" ]; then
        (
            cd $depsdir
            tar xjf $distdir/$lucenename.tar.bz2
            cp $lucenedir/security/*.security $securitydir
        )
    else
        messageWithEnter "The architecture $architecture is not supported by the installation!
    You'll have to manually compile PyLucene."
    fi
fi

messageWithEnter "Installing the packages:
    - Suite-XML-1.0.2
    - Amara-1.2
    - storage-5.0
    - cq2utils-4.3"
packages="4Suite-XML-1.0.2
Amara-1.2a2
storage-5.0
cq2utils-4.4.1
cqlparser-1.3"
for package in $packages; do
    (
        test -d $depsdir/$package && continue
        message "Installing $package"
        test -d $tempdir && rm -rf $tempdir
        mkdir $tempdir
        cd $tempdir
        thepath=
        for d in $(ls -1 $depsdir); do
            test -d $depsdir/$d && thepath=$depsdir/$d:$thepath
        done
        tar xzf $distdir/${package}.tar.gz
        cd ${package}
        PYTHONPATH=$thepath python setup.py install --install-lib $depsdir/$package --prefix $depsdir/$package
        rm -rf $tempdir
    )
done


testresult=/tmp/meresco.testresult
owner=$(stat --format %U $0)
(
rm $testresult -f
test -d $merescodir/deps.d/libgcj5 && export LD_LIBRARY_PATH=$merescodir/deps.d/libgcj5
cd $merescodir/test
su -c "./alltests.py > $testresult 2>&1" $owner
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
