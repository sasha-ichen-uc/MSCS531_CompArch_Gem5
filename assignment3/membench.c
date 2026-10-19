#include <stdio.h>
#include <stdlib.h>

/* Strided array walk: touches ARRAY_BYTES of memory with a fixed stride.
 * Small strides reuse cache lines; large strides miss more. */
#define ARRAY_BYTES (256 * 1024)   /* 256 KiB: larger than a 32 KiB L1 */
#define STRIDE      64             /* bytes between accesses */
#define PASSES      8

int main(void) {
    volatile int *a = malloc(ARRAY_BYTES);
    if (!a) return 1;
    size_t n = ARRAY_BYTES / sizeof(int);
    size_t step = STRIDE / sizeof(int);
    long sum = 0;
    for (int p = 0; p < PASSES; p++)
        for (size_t i = 0; i < n; i += step) {
            a[i] = (int)(i + p);
            sum += a[i];
        }
    printf("sum=%ld\n", sum);
    free((void *)a);
    return 0;
}
