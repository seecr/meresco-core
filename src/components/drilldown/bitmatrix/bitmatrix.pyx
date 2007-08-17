# import types and functions for direct usage to speed up
cdef extern from "Python.h":
	ctypedef extern struct PyObject
	void Py_INCREF(PyObject* o)
	void Py_DECREF(PyObject* o)
	ctypedef extern int Py_ssize_t
	void   PyMem_Free(void *p)
	void*  PyMem_Malloc(int n) except NULL
	int PyList_Append(PyObject *list, PyObject *item)
	PyObject* PyTuple_New(Py_ssize_t n)
	PyObject* PyInt_FromLong(long value)
	PyObject* PyList_New(  Py_ssize_t len)
	void PyTuple_SET_ITEM(  PyObject *p, Py_ssize_t pos, PyObject *o)

cdef extern unsigned int combinedCardinality(unsigned int* lhs, unsigned int* rhs)

# Creates an array with both lenght in byte 0 as well as terminated by 0xFFFFFFFF
cdef unsigned int* pythonListOfIntsToCIntArray(object pyList):
	cdef unsigned int* arrayOfInts
	cdef int i
	arrayOfInts = <unsigned int*> PyMem_Malloc((len(pyList)+2) * sizeof(unsigned int))
	i = 1
	for number in pyList:
		arrayOfInts[i] = number
		i = i + 1
	arrayOfInts[0] = i - 1
	arrayOfInts[i] = 0xFFFFFFFF
	return arrayOfInts

cdef class BitMatrix:

	cdef unsigned int** _rows
	cdef unsigned int _row
	cdef unsigned int _maxRows

	def __init__(self, int numberOfDocs = 0, maxRows = 100):
		self._row = 0
		self._maxRows = maxRows
		self._rows = <unsigned int**> PyMem_Malloc(maxRows * sizeof(unsigned int*))

	def addRow(self, columnNumbers):
		if self._row >= self._maxRows:
			raise Exception('Too many rows, max=%d' % self._maxRows)
		self._rows[self._row] = pythonListOfIntsToCIntArray(columnNumbers)
		self._row = self._row + 1
		return self._row - 1

	def combinedRowCardinalities(self, columnNumbers, int maxresults = 0):
		# beware the ?functionlity? of sortAndTruncateAndGetMinValueInResult !
		cdef unsigned int* mask
		cdef unsigned int c
		cdef unsigned int i
		cdef PyObject *result
		cdef PyObject *t
		mask = pythonListOfIntsToCIntArray(columnNumbers)
		result = PyList_New(0) # new reference
		for i from 0 <= i < self._row:
			c = combinedCardinality(mask, self._rows[i])
			if c:
				t = PyTuple_New(2)
				PyTuple_SET_ITEM(t, 0, PyInt_FromLong(i))
				PyTuple_SET_ITEM(t, 1, PyInt_FromLong(c))
				PyList_Append(result, t)
				Py_DECREF(t)
		PyMem_Free(mask)
		try:
			# PyRex generates INCREF before returning, which isn't needed, so this leaks memory
			# its ugly, but it won't leak this way
			return <object> result
		finally:
			Py_DECREF(result)

	def rowCadinalities(self):
		result = []
		for i from 0 <= i < self._row:
			c = self._rows[i][0]
			if c:
				result.append((i, c))
		return result
