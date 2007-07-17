#!/bin/bash

rm -rf *.o *.so bitarray.py *_wrap.*
swig -c++ -python -shadow bitarray.i

g++ -I/usr/include/python2.4 -fPIC -O3 -c -g -o bitarray_wrap.o bitarray_wrap.cxx
g++ -O3 -c -g -fPIC -o BitArray.o BitArray.cpp
g++ -L/usr/lib/gcc/i486-linux-gnu/4.0.3/ -fPIC -lstdc++ -shared -o _bitarray.so BitArray.o bitarray_wrap.o
