int combinedCardinality1(int* lhs, int* rhs) {
	int result = 0;
	register int* lh_ptr = lhs+1;
	register int* rh_ptr = rhs+1;
	int* lh_top = lhs+*lhs;
	int* rh_top = rhs+*rhs;
	while (lh_ptr <= lh_top && rh_ptr <= rh_top) {
		if (*lh_ptr == *rh_ptr) {
			result++;
			lh_ptr++;
			rh_ptr++;
		} else if (*lh_ptr < *rh_ptr) {
			lh_ptr++;
		} else /* > */ {
			rh_ptr++;
		}
	}
	return result;
}
/* about 20% faster */
int combinedCardinality2(register int* lhs, int* rhs) {
	int result = 0;
	int* lh_top = lhs+*lhs;
	int* rh_top = rhs+*rhs;
	register int v;
	while ( lhs <= lh_top && rhs <= rh_top ) {
		v = *(rhs+1);
		while ( *++lhs < v && lhs <= lh_top);
		v = *lhs;
		while ( *++rhs < v && rhs <= rh_top);
		if (*lhs == *rhs) result++;
	}
	return result;
}
/* with FFFFFF terminated list, about 10% faster */
unsigned int combinedCardinality(register unsigned int* lhs, register unsigned int* rhs) {
	register unsigned int result = 0;
	register unsigned int v = 0;
	while ( v < 0xFFFFFFFF ) {
		v = *(rhs+1);
		while ( *++lhs < v );
		v = *lhs;
		while ( *++rhs < v );
		if ( v == *rhs ) result++;
	}
	return result-1;
}

