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

from xmlpump import Converter
from cqlparser.cqlparser import CQLAbstractSyntaxNode
from cqlparser import CqlIdentityVisitor

class CQLConversion(Converter):
    def __init__(self, astConversion):
        Converter.__init__(self)
        self._astConversion = astConversion

    def _canConvert(self, anObject):
        return isinstance(anObject, CQLAbstractSyntaxNode)

    def _convert(self, cqlAst):
        return self._astConversion(cqlAst)

class CqlSearchClauseConversion(CQLConversion):
    def __init__(self, searchClauseFilter, modifier):
        CQLConversion.__init__(self, self._convertAst)
        self._searchClauseFilter = searchClauseFilter
        self._modifier = modifier
        
    def _convertAst(self, ast):
        return CqlSearchClauseModification(ast, self._searchClauseFilter, self._modifier).visit()

class CqlSearchClauseModification(CqlIdentityVisitor):
    def __init__(self, ast, searchClauseFilter, modifier):
        CqlIdentityVisitor.__init__(self, ast)
        self._searchClauseFilter = searchClauseFilter
        self._modifier = modifier

    def visitSEARCH_CLAUSE(self, node):
        if self._searchClauseFilter(node):
            return self._modifier(node)
        return CqlIdentityVisitor.visitSEARCH_CLAUSE(self, node)
