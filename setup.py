## begin license ##
#
#    Meresco Core is an open-source library containing components to build 
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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
from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(
    name='meresco',
    packages=[
        'meresco',
        'meresco.components',
        'meresco.components.drilldown',
        'meresco.components.drilldown.cpp',
        'meresco.components.http',
        'meresco.components.lucene',
        'meresco.components.oai',
        'meresco.components.sru',
        'meresco.components.xml_generic',
        'meresco.legacy',
        'meresco.legacy.plugins',
        'meresco.framework'
    ],
    package_data={
        'meresco.components': ['*.rules'],
        'meresco.components.oai': ['data/*'],
        'meresco.components.xml_generic': [
            'schemas/*',
            'schemas-lom/*.xsd',
            'schemas-lom/common/*',
            'schemas-lom/examples/*',
            'schemas-lom/extend/*',
            'schemas-lom/unique/*',
            'schemas-lom/vocab/*'
        ]
    },
    ext_modules=[
        Extension("meresco.components.drilldown.cpp._bitarray", [
		"meresco/components/drilldown/cpp/bitarray_wrap.cxx",
		"meresco/components/drilldown/cpp/BitArray.cpp"]
		),
        Extension("meresco.components.drilldown.bitmatrix", [
		"meresco/components/drilldown/bitmatrix/bitmatrix.pyx",
		"meresco/components/drilldown/bitmatrix/bitmatrix_misc.c"],
        extra_compile_args = ['-O3']
		)
    ],
    cmdclass = {'build_ext': build_ext}
)
