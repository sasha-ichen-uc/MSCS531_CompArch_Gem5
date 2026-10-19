/* branch_heavy.c - Branch-intensive workload with unpredictable patterns.
 * Uses data-dependent branches that are hard to predict.
 * Compile: zig cc -target x86_64-linux-musl -static -O1 -o branch_heavy branch_heavy.c
 */
#include <stdio.h>

#define N 2000

int main(void) {
    int data[N];
    long sum = 0;

    /* pseudo-random fill using LCG */
    unsigned int seed = 12345;
    for (int i = 0; i < N; i++) {
        seed = seed * 1103515245 + 12345;
        data[i] = (int)((seed >> 16) & 0x7FFF);
    }

    /* highly unpredictable branches */
    for (int pass = 0; pass < 20; pass++) {
        for (int i = 0; i < N; i++) {
            int val = data[i];
            if (val % 7 < 3)
                sum += val;
            else if (val % 11 < 5)
                sum -= val / 2;
            else if (val % 13 < 6)
                sum += val * 2;
            else
                sum ^= val;
        }
    }

    printf("branch_heavy result: %ld\n", sum);
    return 0;
}
