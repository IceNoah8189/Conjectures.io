/*
 * Erdős 686 witness search.
 * Find k >= 2, n >= 0, m >= n + k with
 *     (m+1)(m+2)...(m+k) = R * (n+1)(n+2)...(n+k).
 *
 * Usage: search R k n_start n_end
 *
 * For each n, the unique m with A(m) closest to R*A(n) is tracked with a
 * two-pointer sweep on long-double logarithms (A is increasing in m). The
 * candidates m-1, m, m+1 are then tested exactly modulo two 61-bit primes.
 * Every surviving candidate is printed as "HIT R k n m" and must be confirmed
 * with exact integer arithmetic (verify.py). Logs are recomputed from scratch
 * periodically so rounding drift stays far below one step.
 * Progress lines "PROGRESS k n" go to stderr.
 */
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

typedef unsigned __int128 u128;
static const uint64_t P1 = 2305843009213693951ULL; /* 2^61 - 1 */
static const uint64_t P2 = 2305843009213693921ULL; /* prime below 2^61 */

static uint64_t mulmod(uint64_t a, uint64_t b, uint64_t p) {
    return (uint64_t)((u128)a * b % p);
}

static uint64_t prodmod(uint64_t start, int k, uint64_t p) {
    uint64_t r = 1;
    for (int i = 1; i <= k; i++) r = mulmod(r, (start + i) % p, p);
    return r;
}

static long double logprod(uint64_t start, int k) {
    long double s = 0;
    for (int i = 1; i <= k; i++) s += logl((long double)(start + i));
    return s;
}

static int exact_mod(uint64_t R, int k, uint64_t n, uint64_t m) {
    uint64_t t1 = mulmod(R % P1, prodmod(n, k, P1), P1);
    if (prodmod(m, k, P1) != t1) return 0;
    uint64_t t2 = mulmod(R % P2, prodmod(n, k, P2), P2);
    return prodmod(m, k, P2) == t2;
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "usage: %s R k n_start n_end\n", argv[0]);
        return 2;
    }
    uint64_t R = strtoull(argv[1], 0, 10);
    int k = atoi(argv[2]);
    uint64_t n0 = strtoull(argv[3], 0, 10), n1 = strtoull(argv[4], 0, 10);
    long double logR = logl((long double)R);

    uint64_t n = n0;
    long double lt = logR + logprod(n, k); /* log target */
    /* smallest admissible m is n + k; start there and advance */
    uint64_t m = n + k;
    long double lm = logprod(m, k);
    uint64_t steps = 0;

    for (; n <= n1; n++) {
        if (m < n + k) { m = n + k; lm = logprod(m, k); }
        /* advance m while A(m+1) <= target (in logs) */
        for (;;) {
            long double next = lm + logl((long double)(m + k + 1)) - logl((long double)(m + 1));
            if (next <= lt) { m++; lm = next; } else break;
        }
        /* now A(m) <= target < A(m+1) up to rounding. Only m or m+1 can be
         * exact; test each exactly only if its log is within EPS of the
         * target. Rounding drift (recomputed every 4096 steps) is ~1e-15. */
        long double up = lm + logl((long double)(m + k + 1)) - logl((long double)(m + 1));
        const long double EPS = 1e-11L;
        for (int d = 0; d <= 1; d++) {
            uint64_t mm = m + d;
            long double gap = d ? up - lt : lt - lm;
            if (mm < n + k || gap > EPS) continue;
            if (exact_mod(R, k, n, mm)) {
                printf("HIT %" PRIu64 " %d %" PRIu64 " %" PRIu64 "\n", R, k, n, mm);
                fflush(stdout);
            }
        }
        /* move to n+1 */
        if (++steps % 4096 == 0) {
            lt = logR + logprod(n + 1, k);
            lm = logprod(m, k);
        } else {
            lt += logl((long double)(n + k + 1)) - logl((long double)(n + 1));
        }
    }
    fprintf(stderr, "DONE %" PRIu64 " %d %" PRIu64 " %" PRIu64 "\n", R, k, n0, n1);
    return 0;
}
