/* fp_compute.c - Floating-point-heavy workload.
 * Exercises FP add, multiply, divide, and iterative sqrt operations.
 * Uses integer printf to avoid musl libc FP-format stack overflow in gem5 SE.
 * Compile: zig cc -target x86_64-linux-musl -static -O1 -o fp_compute fp_compute.c
 */
#include <stdio.h>

#define N 500

/* Iterative Newton-Raphson sqrt (avoids libm) */
static double my_sqrt(double x) {
    if (x <= 0.0) return 0.0;
    double guess = x * 0.5;
    for (int i = 0; i < 10; i++)
        guess = 0.5 * (guess + x / guess);
    return guess;
}

int main(void) {
    static double a[N], b[N], c[N];

    for (int i = 0; i < N; i++) {
        a[i] = (double)(i + 1) * 0.01;
        b[i] = (double)(N - i) * 0.02;
    }

    /* FP-heavy: multiply, add, divide, sqrt */
    for (int pass = 0; pass < 20; pass++) {
        for (int i = 0; i < N; i++) {
            c[i] = a[i] * b[i] + my_sqrt(a[i]) - b[i] / (a[i] + 1.0);
        }
    }

    double sum = 0.0;
    for (int i = 0; i < N; i++)
        sum += c[i];

    /* Print scaled integer to avoid FP-format printf stack explosion */
    printf("fp_compute result: %ld (x1e6)\n", (long)(sum * 1000000.0));
    return 0;
}
