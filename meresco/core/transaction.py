# -*- coding: utf-8 -*-
## begin license ##
# 
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives. 
# 
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2010-2011 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2011-2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Meresco Core"
# 
# "Meresco Core" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Meresco Core" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Meresco Core"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##


class TransactionException(Exception):
    pass

class Transaction(object):
    def __init__(self, name):
        self._resourceManagers = []
        self.locals = {}
        self.name = name

    def getId(self):
        return id(self)

    def join(self, resourceManager):
        if resourceManager not in self._resourceManagers:
            self._resourceManagers.append(resourceManager)

    def commit(self):
        while self._resourceManagers:
            resourceManager = self._resourceManagers.pop(0)
            yield resourceManager.commit(id=self.getId())

    def rollback(self):
        while self._resourceManagers:
            resourceManager = self._resourceManagers.pop(0)
            yield resourceManager.rollback(id=self.getId())

    def abort(self):
        raise TransactionException()

    def objectScope(self, o):
        return self.locals.setdefault('%s@%s' % (o.__class__.__name__, id(o)), {})
