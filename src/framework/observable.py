## begin license ##
#
#    "CQ2 Utils" (cq2utils) is a package with a wide range of valuable tools.
#    Copyright (C) 2005, 2006 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of "CQ2 Utils".
#
#    "CQ2 Utils" is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    "CQ2 Utils" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "CQ2 Utils"; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from traceback import format_exception
from sys import exc_info

class Defer:
	def __init__(self, observable, defereeType):
		self._observable = observable
		self._defereeType = defereeType
	
	def __getattr__(self, attr):
		return self._defereeType(self._observable._observers, attr)

class DeferredFunction:
	def __init__(self, delegates, attr):
		self._delegates = delegates
		self._attr = attr
		
class AllFunction(DeferredFunction):
	def __call__(self, *args, **kwargs):
		result = None
		for delegate in self._delegates:
			if hasattr(delegate, self._attr):
				result = getattr(delegate, self._attr)(*args, **kwargs) or result
		return result

class AnyFunction(DeferredFunction):
	def __call__(self, *args, **kwargs):
		result = None
		for delegate in self._delegates:
			if hasattr(delegate, self._attr):
				result = getattr(delegate, self._attr)(*args, **kwargs)
				if result:
					return result
		return result

class Observable(object):
	def __init__(self, name = None):
		self._observers = []
		self.all = Defer(self, AllFunction)
		self.any = Defer(self, AnyFunction)
		if name:
			self.__repr__ = lambda: name

	def addObserver(self, observer):
		self._observers.append(observer)

	def addObservers(self, tree):
		for node in tree:
			if isinstance(node, tuple):
				node, branch = node
				node.addObservers(branch)
			self.addObserver(node)
			
	def _notifyObservers(self, __returnResult__, *args, **kwargs):
		i = 0
		while i < len(self._observers):
			result = self._observers[i].notify(*args, **kwargs)
			if __returnResult__ and result != None:
				return result
			i += 1
				
	def changed(self, *args, **kwargs):
		return self._notifyObservers(False, *args, **kwargs)
				
	def process(self, *args, **kwargs):
		return self._notifyObservers(True, *args, **kwargs)

class Function:
	
	def __init__(self, observable):
		self._observable = observable
		self._observable.addObserver(self)
		
	def notify(self, *args, **kwargs):
		self._result = args #kwargs is nog een vraagteken voor mij (KVS)
		if len(self._result) == 0:
			self._result = None
		elif len(self._result) == 1:
			self._result = self._result[0]
		
	def __call__(self, *args, **kwargs):
		self._observable.notify(*args, **kwargs) # hier is **kwargs triviaal
		return self._result
		
class FunctionObservable(Observable):
	#ik weet het, YAGNI, maar het is zooooo mooi symmetrisch - wilde toch even laten zien dat dit het soort dingen is wat we kunnen doen en denk dat we het nut vrij snel tegenkomen. Zo niet dan mag hij in het vuilnisvat
	
	def __init__(self, function):
		Observable.__init__(self)
		self._function = function
	
	def notify(self, *args, **kwargs):
		results = self._function(*args, **kwargs)
		self.changed(*results)
