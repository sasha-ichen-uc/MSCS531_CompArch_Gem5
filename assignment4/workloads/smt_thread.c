/* smt_thread.c - Simple single-threaded workload for SMT experiments.
 * Run two instances of this simultaneously to test SMT resource sharing.
 * Compile: zig cc -target x86_64-linux-musl -static -O1 -o smt_thread smt_thread.c
 */
#include <stdio.h>

#define N 1000

int main(void) {
    int arr[N];
    long sum = 0;

    for (int i = 0; i < N; i++)
        arr[i] = i * 3 + 1;

    for (int pass = 0; pass < 15; pass++) {
        for (int i = 0; i < N; i++) {
            sum += arr[i] * (i % 5 + 1);
            if (i > 0)
                arr[i] = (arr[i] + arr[i - 1]) / 2;
        }
    }

    printf("smt_thread result: %ld\n", sum);
    return 0;
}
