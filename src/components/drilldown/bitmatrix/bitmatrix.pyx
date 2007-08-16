# import types and functions for direct usage to speed up
cdef extern from "Python.h":
	ctypedef extern struct PyObject
	ctypedef extern int Py_ssize_t
	void   PyMem_Free(void *p)
	void*  PyMem_Malloc(int n) except NULL
	int PyList_Append(PyObject *list, PyObject *item)
	PyObject* PyTuple_Pack(Py_ssize_t n, PyObject *a, PyObject *b)
	PyObject* PyInt_FromLong(long value)
	PyObject* PyList_New(  Py_ssize_t len)

cdef extern unsigned int combinedCardinality(unsigned int* lhs, unsigned int* rhs)

cdef unsigned int* pythonListOfIntsToCIntArray(object pyList):
	cdef unsigned int* arrayOfInts
	cdef int i
	arrayOfInts = <unsigned int*> PyMem_Malloc(100002 * sizeof(unsigned int))
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

	def __init__(self, int numberOfDocs = 0):
		self._row = 0
		self._rows = <unsigned int**> PyMem_Malloc(10000 * sizeof(unsigned int*))

	def addRow(self, columnNumbers):
		self._rows[self._row] = pythonListOfIntsToCIntArray(columnNumbers)
		self._row = self._row + 1
		return self._row - 1

	def combinedRowCardinalities(self, columnNumbers, int maxresults = 0):
		# beware the ?functionlity? of sortAndTruncateAndGetMinValueInResult !
		cdef unsigned int* mask
		cdef unsigned int c
		cdef unsigned int i
		cdef PyObject *result
		mask = pythonListOfIntsToCIntArray(columnNumbers)
		result = PyList_New(0)
		for i from 0 <= i < self._row:
			c = combinedCardinality(mask, self._rows[i])
			if c:
				PyList_Append(result, PyTuple_Pack(2, PyInt_FromLong(i), PyInt_FromLong(c)))
			#result.append((i, c))
		PyMem_Free(mask)
		return <object> result

	def rowCadinalities(self):
		result = []
		for i from 0 <= i < self._row:
			c = self._rows[i][0]
			result.append((i, c))
		return result
