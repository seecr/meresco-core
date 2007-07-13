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

from meresco.framework.observable import Observable

class TypedObservable(Observable):
	
	def __init__(self):
		Observable.__init__(self)
		
	def __implements__(self):
		return {}
	
	def __requires__(self):
		return {}
	
	def addObserver(self, observer):
		if isinstance(observer, TypedObservable):
			requiredMethods = self.__requires__()
			implementedMethods = observer.__implements__()
			for name, requiredSignature in requiredMethods.items():
				if name in implementedMethods:
					implentedSignature = implementedMethods[name]
					if implentedSignature == requiredSignature:
						Observable.addObserver(self, observer)
					else:
						converter = getConverter(name, requiredSignature, implentedSignature)
						convertingObservable = ConvertingObservable(name, converter)
						Observable.addObserver(self, convertingObservable)
						convertingObservable.addObserver(observer)
				else:
					return
					Observable.addObserver(self, observer) #what to do for unknown conversion?!
		else:
			Observable.addObserver(self, observer)
			

class ConvertingObservableFunction:
	
	def __init__(self, realSelf, methodName, converter):
		self._realSelf = realSelf
		self._methodName = methodName
		self._converter = converter
		
	def __call__(self, *args):
		method = self._realSelf.all.__getattr__(self._methodName)(*(self._converter(*args)))

class ConvertingObservable(Observable):
	
	def __init__(self, methodName, converter):
		Observable.__init__(self)
		self.__dict__[methodName] = ConvertingObservableFunction(self, methodName, converter)
			
converters = {}

def registerConverter(methodName, fromSignature, toSignature, converter):
	if not converters.has_key(methodName):
		converters[methodName] = {}
	if not converters[methodName].has_key(fromSignature):
		converters[methodName][fromSignature] = {}
	converters[methodName][fromSignature][toSignature] = converter

def clearConverters():
	converters.clear()
	
def getConverter(methodName, fromSignature, toSignature):
	try:
		return converters[methodName][fromSignature][toSignature]
	except:
		raise Exception("No converter found for method %s from type %s to %s") % (methodName, fromSignature, toSignature)