/* mem_compute.c - Memory-intensive workload with strided and random access.
 * Exercises cache hierarchy and memory pipeline.
 * Compile: zig cc -target x86_64-linux-musl -static -O1 -o mem_compute mem_compute.c
 */
#include <stdio.h>
#include <stdlib.h>

#define ARRAY_SIZE (64 * 1024)   /* 256 KiB of ints: larger than L1 */

int main(void) {
    int *arr = (int *)malloc(ARRAY_SIZE * sizeof(int));
    if (!arr) return 1;

    /* init */
    for (int i = 0; i < ARRAY_SIZE; i++)
        arr[i] = i;

    long sum = 0;

    /* strided access (cache-line skipping) */
    for (int pass = 0; pass < 5; pass++) {
        for (int i = 0; i < ARRAY_SIZE; i += 16) {  /* stride = 64 bytes */
            sum += arr[i];
            arr[i] = (int)(sum & 0xFFFF);
        }
    }

    /* pointer-chasing (pseudo-random access) */
    int idx = 0;
    for (int i = 0; i < 20000; i++) {
        idx = (idx + arr[idx % ARRAY_SIZE] + 17) % ARRAY_SIZE;
        sum += arr[idx];
    }

    printf("mem_compute result: %ld\n", sum);
    free(arr);
    return 0;
}
