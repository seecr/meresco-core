/* Algoritm: zipper. Assumes 0xFFFFFFFF terminated lists */
unsigned int combinedCardinality(register unsigned int* lhs, register unsigned int* rhs) {
	register unsigned int result = 0;
	lhs++;
	rhs++;
	if ( *lhs > *rhs ) {
		while ( *lhs < 0xFFFFFFFF ) {
			if ( *lhs == *rhs ) result++;
			while ( *++rhs < *lhs );
			if ( *lhs == *rhs ) result++;
			while ( *++lhs < *rhs );
		}
	}
	else {
		while ( *rhs < 0xFFFFFFFF ) {
			if ( *lhs == *rhs ) result++;
			while ( *++lhs < *rhs );
			if ( *lhs == *rhs ) result++;
			while ( *++rhs < *lhs );
		}
	}
	return result;
}
