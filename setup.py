## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
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

setup(
    name='meresco-core',
    packages=[
        'merescocore',
        'merescocore.components',
        'merescocore.components.drilldown',
        'merescocore.components.http',
        'merescocore.components.numeric',
        'merescocore.components.sru',
        'merescocore.components.xml_generic',
        'merescocore.framework',
    ],
    package_data={
        'merescocore.components': ['rules/*.rules'],
        'merescocore.components.xml_generic': [
            'schemas/*',
            'schemas-lom/*.xsd',
            'schemas-lom/common/*',
            'schemas-lom/examples/*',
            'schemas-lom/extend/*',
            'schemas-lom/unique/*',
            'schemas-lom/vocab/*'
        ]
    },
    version='%VERSION%',
    url='http://www.meresco.org',
    author='Seek You Too',
    author_email='info@cq2.nl',
    description='Meresco Core is an open-source library containing components to build searchengines, repositories and archives.',
    long_description='Meresco Core is an open-source library containing components to build searchengines, repositories and archives.',
    license='GNU Public License',
    platforms='all',

)
