# -*- coding: utf-8 -*-
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

from cqlparser import CqlIdentityVisitor

class RenameCqlIndex(object):
    def __init__(self, fieldRename):
        self._fieldRename = fieldRename

    def __call__(self, cqlAst):
        return _CqlIndexChangeVisitor(self._fieldRename, cqlAst).visit()

class _CqlIndexChangeVisitor(CqlIdentityVisitor):
    def __init__(self, fieldRename, root):
        CqlIdentityVisitor.__init__(self, root)
        self._fieldRename = fieldRename

    def visitINDEX(self, node):
        assert len(node.children()) == 1
        myterm = node.children()[0]
        return node.__class__(myterm.__class__(self._fieldRename(myterm.children()[0])))

