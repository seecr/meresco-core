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

set -o errexit

basedir=$(dirname $0)

source $basedir/functions.sh

echo "*
* Checking installation of daemontools."

if isDebian ; then
	if [ ! -f /usr/bin/svc ]; then
		echo "* Installing daemaontools."
		aptitude install daemontools-installer
echo "* You will be asked a couple of questions.
* The default answer should be good enough.
[Press Enter to continue]"
		read
		build-daemontools
	fi
else
  # if svc is not in its common place (non debian common place) then download 
  # the official package and patch it. Then compile and install it as
  # instructed on http://cr.yp.to
	if [ ! -f /command/svc ]; then
		echo "* Downloading and compiling deamontools"
		mkdir --parents /package
		chmod 1755 /package
		cd /package
		wget http://download.cq2.org/third-party/daemontools-0.76.tar.gz
		gunzip daemontools-0.76.tar
		tar -xpf daemontools-0.76.tar
		rm -f daemontools-0.76.tar
		cd admin/daemontools-0.76
		sed --in-place 's,extern int errno;,#include <errno.h>,g' src/error.h
		package/install
	fi
fi
