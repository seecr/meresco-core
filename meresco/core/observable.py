## begin license ##
# 
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives. 
# 
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

from weightless.core import Observable as Observable_orig, Transparent as Transparent_orig, local


class Context(object):
    def __getattr__(self, name):
        try:
            return local('__callstack_var_%s__' % name)
        except AttributeError:
            raise AttributeError("'%s' has no attribute '%s'" % (self, name))


class Observable(Observable_orig):
    def __init__(self, name=None):
        Observable_orig.__init__(self, name=name)
        self.ctx = Context()


class Transparent(Transparent_orig):
    def __init__(self, name=None):
        Transparent_orig.__init__(self, name=name)
        self.ctx = Context()

