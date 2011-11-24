## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2010 Stichting Kennisnet http://www.kennisnet.nl
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

from os import system                              #DO_NOT_DISTRIBUTE
from sys import path as sysPath                    #DO_NOT_DISTRIBUTE
system('find .. -name "*.pyc" | xargs rm -f')      #DO_NOT_DISTRIBUTE
                                                   #DO_NOT_DISTRIBUTE
from glob import glob                              #DO_NOT_DISTRIBUTE
for path in glob('../deps.d/*'):                   #DO_NOT_DISTRIBUTE
    sysPath.insert(0, path)                        #DO_NOT_DISTRIBUTE
                                                   #DO_NOT_DISTRIBUTE
sysPath.insert(0, "..")                            #DO_NOT_DISTRIBUTE

import unittest

from helixtest import HelixTest
from generatorutilstest import GeneratorUtilsTest
from observabletest import ObservableTest
from transactiontest import TransactionTest
print 'BatchTransactionScopeTest is disabled for now!'
#from batchtransactionscopetest import BatchTransactionScopeTest

if __name__ == '__main__':
    unittest.main()
