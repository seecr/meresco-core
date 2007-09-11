## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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
from sys import exc_info
from types import GeneratorType

def compose(generator):
    try:
        for value in generator:
            if type(value) == GeneratorType:
                for nested in compose(value):
                    yield nested
            else:
                yield value
    except:
        exType, exValue, exTraceback = exc_info()
        raise exType, exValue, exTraceback.tb_next # skip myself from traceback

def decorate(before, generator, after):
    first = generator.next()
    yield before
    yield first
    for value in generator:
        yield value
    yield after

class Peek:

	def __init__(self, generator):
		self._generator = generator
		try:
			self._first = generator.next()
		except StopIteration:
			pass

	def empty(self):
		return not hasattr(self, '_first')

	def __iter__(self):
		while True:
			yield self._first
			self._first = self._generator.next()

