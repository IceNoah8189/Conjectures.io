#!/usr/bin/env python3
"""Exactly verify "HIT R k n m" lines (stdin or files): prod(m+i) == R*prod(n+i), m >= n+k, k >= 2."""
import fileinput
from math import prod

for line in fileinput.input():
    p = line.split()
    if not p or p[0] != "HIT":
        continue
    R, k, n, m = map(int, p[1:5])
    ok = k >= 2 and m >= n + k and prod(m + i for i in range(1, k + 1)) == R * prod(n + i for i in range(1, k + 1))
    print(("VERIFIED" if ok else "FALSE-POSITIVE"), R, k, n, m, flush=True)
