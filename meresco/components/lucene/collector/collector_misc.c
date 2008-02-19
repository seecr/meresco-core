#include <stdlib.h>

int * createArray(int size) {
    return (int *) calloc (size, sizeof(int));
}

void freeArray(int *array) {
    free(array);
}

int addDoc(int *array, int offset, int doc) {
    array[offset++] = doc;
    return offset;
}
