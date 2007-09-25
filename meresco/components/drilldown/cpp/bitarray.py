# This file was created automatically by SWIG 1.3.28.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _bitarray
import new
new_instancemethod = new.instancemethod
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'PySwigObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


class DenseBitArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, DenseBitArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, DenseBitArray, name)
    def __repr__(self):
        try: strthis = "at 0x%x" %( self.this, ) 
        except: strthis = "" 
        return "<%s.%s; proxy of C++ DenseBitArray instance %s>" % (self.__class__.__module__, self.__class__.__name__, strthis,)
    def __init__(self, *args):
        this = _bitarray.new_DenseBitArray(*args)
        try: self.this.append(this)
        except: self.this = this
    def cardinality(*args): return _bitarray.DenseBitArray_cardinality(*args)
    def set(*args): return _bitarray.DenseBitArray_set(*args)
    def get(*args): return _bitarray.DenseBitArray_get(*args)
    def combinedCardinality(*args): return _bitarray.DenseBitArray_combinedCardinality(*args)
    __swig_destroy__ = _bitarray.delete_DenseBitArray
    __del__ = lambda self : None;
_bitarray.DenseBitArray_swigregister(DenseBitArray)

class SparseBitArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SparseBitArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SparseBitArray, name)
    def __repr__(self):
        try: strthis = "at 0x%x" %( self.this, ) 
        except: strthis = "" 
        return "<%s.%s; proxy of C++ SparseBitArray instance %s>" % (self.__class__.__module__, self.__class__.__name__, strthis,)
    def __init__(self, *args):
        this = _bitarray.new_SparseBitArray(*args)
        try: self.this.append(this)
        except: self.this = this
    def cardinality(*args): return _bitarray.SparseBitArray_cardinality(*args)
    def set(*args): return _bitarray.SparseBitArray_set(*args)
    def combinedCardinality(*args): return _bitarray.SparseBitArray_combinedCardinality(*args)
    __swig_destroy__ = _bitarray.delete_SparseBitArray
    __del__ = lambda self : None;
_bitarray.SparseBitArray_swigregister(SparseBitArray)



