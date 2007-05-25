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

set -o errexit

basedir=$(cd $(dirname $0); pwd)
source $basedir/functions.sh

isroot

if [ $# -ne 3 ]; then 
	echo "Usage: $0 <cq2_dep_dir> <package_name> <package_version>"
	exit 1
fi
cq2_dep_dir=$1
package_name=$2
package_version=$3

package_dir=$cq2_dep_dir/$package_name

if [ ! -d $package_dir ]; then
	pack=$basedir/../dist/${package_name}_${package_version}.tar.gz
	mkdir -p $cq2_dep_dir
	tar --directory $cq2_dep_dir -xzf $pack
	mv $cq2_dep_dir/${package_name}_${package_version}/${package_name} $cq2_dep_dir/${package_name}
	rm -rf $cq2_dep_dir/${package_name}_${package_version}
fi
	
