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


function isroot {
 if [ $(id -u) -ne 0 ]; then
  echo "Need to be root"
  exit -1
 fi
}

function isSuSE {
	test -e /etc/SuSE-release
}
	
function isFedora {
	test -e /etc/fedora-release
}
		
function isDebian {
	test -e /etc/debian_version
}

PM_INSTALL="UNDEFINED"
isDebian && export PM_INSTALL="aptitude install"
isSuSE && export PM_INSTALL="yast --install"
isFedora && export PM_INSTALL="yum install"
			
function configureIpTables {
	local firewall_name=$1
	shift
	local ports=$*
	echo "*
* Opening ports: $ports"
	firewall_file="/etc/network/if-up.d/firewall_$firewall_name"
	echo "#!/bin/sh
IPTABLES=/sbin/iptables" > $firewall_file
	for port in $ports; do
		echo "\$IPTABLES --list --numeric | grep \"ACCEPT.*tcp.*dpt\:$port \"|| \$IPTABLES -A INPUT -i eth0 -p tcp --dport $port -j ACCEPT" >> $firewall_file
	done
	chmod +x $firewall_file
	$firewall_file
}

function message {
	echo "*
* $1"
}

function aptitude_install {
	repository=$1
	distro=$2
	component=$3
	shift 3
	package=$*
	APTFILE=/etc/apt/sources.list.d/$distro'_'$component.list
	message "Adding temporary repository to APT ($repository $distro $component)"
	echo "deb $repository $distro $component" > $APTFILE
	aptitude update
	aptitude install $package
	message "Removing temporary repository ($repository $distro $component)"
	rm $APTFILE
	aptitude update
}
