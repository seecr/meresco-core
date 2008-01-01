## begin license ##
#
#    CQLParser is parser that builts up a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of CQLParser
#
#    CQLParser is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    CQLParser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CQLParser; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from cqlparser import CqlVisitor

class ClauseCollector(CqlVisitor):

    def __init__(self, astTree, logger):
        CqlVisitor.__init__(self, astTree)
        self._logger = logger

    def visitSCOPED_CLAUSE(self, node):
        result = CqlVisitor.visitSCOPED_CLAUSE(self, node)[0]
        if len(result) == 1:
            self._logger(clause = result[0])
        else:
            if result[0] == "(":
                return result[1]
            self._logger(clause = "%s %s %s" % (result[0][0], result[1], result[2]))
        return result

    def visitRELATION(self, node):
        result = CqlVisitor.visitRELATION(self, node)
        if len(result) == 1:
            return result[0]
        return "%s%s%s" % (result[0], result[1][0][0], result[1][0][2])
