## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
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

if not __debug__:
    raise AssertionError("Do not use optimized code, because Meresco uses assert statements. (See http://docs.python.org/release/2.5.2/ref/assert.html)")

from sys import getdefaultencoding as _getdefaultencoding
from locale import getdefaultlocale, _parse_localename
assert _getdefaultencoding() == 'utf-8', 'Please ensure that the default encoding is utf-8'
assert getdefaultlocale() == _parse_localename('en_US.UTF-8'), "We expect the default locale to be set to utf-8, e.g. use the environment setting LANG=en_US.UTF-8"

from observable import Observable, Transparent

from generatorutils import decorate, decorateWith, functionAsGenerator
from helix import findHelix, link
from transaction import TransactionException, Transaction
from transactionscope import TransactionScope
from resourcemanager import ResourceManager
from batchtransactionscope import BatchTransactionScope

