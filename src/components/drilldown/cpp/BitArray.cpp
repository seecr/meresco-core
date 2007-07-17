#include "BitArray.h"
#include "bitcount.h"

/*
future optimizations:
Dense Bit Array: change values to a array of 2bytes and work 16-based (may be factor 2 improvement)
*/

DenseBitArray::DenseBitArray(size_t size) {
	_len = size;
	_cardinality = 0;
	values.resize(bitToByte(size), 0);
}

size_t DenseBitArray::bitToByte(size_t v) {
	//Returns the number of bytes required to represent v bits
	if (v & 0x7) //all cases except those with 3 trailing zero's, i.e. except 8, 16, 24. Those cases require exactly one more byte than the ones with only zero's, i.e. 9, 10, 11 etc. require one more byte than 8.
		return (v >> 3) + 1;
	else //8, 16, etc. require exactly 1, 2, etc. bytes
		return v >> 3;
}

void DenseBitArray::set(size_t pos) {
	//every bit may only be set once! (assumption)
	_cardinality++;
	size_t wordPos = pos / 8;
	size_t bitPos = pos % 8;
	values[wordPos] |= (1 << bitPos);
}

bool DenseBitArray::get(size_t pos) {
	size_t wordPos = pos / 8;

	// Possible performance hazzard, but for now it keeps us from crashing. 20060706-JJ
	if (values.size() < wordPos) {
		return 0;
	}
        
	size_t bitPos = pos % 8;
	return (values[wordPos] & (1 << bitPos)) != 0;
}

size_t DenseBitArray::combinedCardinality(DenseBitArray other) {
	//assert sizes are equal doen we dus ook niet
	size_t result = 0;
	int byteSize = values.size();
	
	//for extreme optimizations we can do without the following 3 lines:
	if (other.values.size() < byteSize) {
		byteSize = other.values.size();
	}

	for (int i = 0; i < byteSize; i++) {
		unsigned char b = other.values[i] & values[i];
		result += bitcounts[b];
	}
	return result;
}

size_t DenseBitArray::combinedCardinality(SparseBitArray other) {
	return other.combinedCardinality(*this);
}


SparseBitArray::SparseBitArray(size_t maxCardinality) {
	_cardinality = 0;
	values.resize(maxCardinality, 0);
}

void SparseBitArray::set(size_t pos) {
	//bits may only be set left to right (untested assumption)
	values[_cardinality++] = pos;
}

size_t SparseBitArray::combinedCardinality(SparseBitArray other) {
	size_t result = 0;
	size_t myI = 0;
	size_t otherI = 0;
	while (myI < _cardinality && otherI < other._cardinality) {
		if (values[myI] == other.values[otherI]) {
			result++;
			myI++;
			otherI++;
		} else if (values[myI] < other.values[otherI]) {
			myI++;
		} else /* > */ {
			otherI++;
		}
	}
	return result;
}

size_t SparseBitArray::combinedCardinality(DenseBitArray other) {
	size_t result = 0;
	for (size_t i = 0; i < _cardinality; i++) {
		if (other.get(values[i]))
			result++;
	}
	return result;
}
