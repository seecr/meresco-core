## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2012, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
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

from sys import exc_info
from functools import wraps
from weightless.core.utils import isgeneratorfunction

def decorate(before, generator, after):
    try:
        first = next(generator)
    except StopIteration:
        return
    yield before
    yield first
    for value in generator:
        yield value
    yield after

def decorateWith(before, after):
    def _internal(g):
        def newg(*args, **kwargs):
            return decorate(before,
                            g(*args, **kwargs),
                            after)
        return newg
    return _internal

def asyncreturn(g):
    @wraps(g)
    def newg(*args, **kwargs):
        assert not isgeneratorfunction(g), 'Only use for non-generators.'
        return g(*args, **kwargs)
        yield
    return newg

def asyncnoreturnvalue(g):
    @wraps(g)
    def newg(*args, **kwargs):
        _ = g(*args, **kwargs)
        assert _ is None, "Only use for functions that don't return anything."
        return
        yield
    return newg


