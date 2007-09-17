#include <valarray>

class SparseBitArray;

class DenseBitArray {
	private:
		std::valarray<unsigned char> values;
		size_t _len, _cardinality;
		size_t bitToByte(size_t v);
	
	public:
		DenseBitArray(size_t size);
		size_t cardinality(void) { return _cardinality; }
		void set(size_t pos);
		bool get(size_t pos);
		size_t combinedCardinality(DenseBitArray other);
		size_t combinedCardinality(SparseBitArray other);
};

class SparseBitArray {
	private:
		std::valarray<size_t> values;
		size_t _cardinality;
	
	public:
		SparseBitArray(size_t size);
		size_t cardinality(void) { return _cardinality; }
		void set(size_t pos);
		size_t combinedCardinality(DenseBitArray other);
		size_t combinedCardinality(SparseBitArray other);
};
