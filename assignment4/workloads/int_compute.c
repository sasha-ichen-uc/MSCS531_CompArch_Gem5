/* int_compute.c - Integer-heavy workload with loops and branches.
 * Exercises ALU, control flow, and data dependencies.
 * Compile: zig cc -target x86_64-linux-musl -static -O1 -o int_compute int_compute.c
 */
#include <stdio.h>

#define N 1000

int main(void) {
    int arr[N];
    long sum = 0;

    /* fill with a pattern that exercises branches */
    for (int i = 0; i < N; i++)
        arr[i] = (i * 7 + 3) % 13;

    /* branchy reduction: different paths for even/odd/multiples-of-3 */
    for (int pass = 0; pass < 10; pass++) {
        for (int i = 0; i < N; i++) {
            if (arr[i] % 2 == 0)
                sum += arr[i] * 3;
            else if (arr[i] % 3 == 0)
                sum -= arr[i];
            else
                sum += arr[i] + 1;
        }
    }

    printf("int_compute result: %ld\n", sum);
    return 0;
}
