# Independent exact computation of g(t)

`exact_g.py` builds the lattice directly using integer products. Each point
has a Boolean omission variable; each forbidden corner requires at least
one of its three variables to be true. Z3 solves the resulting Boolean
hitting-set problem as MaxSAT: each retained point is a unit-weight soft
constraint, while every corner constraint is mandatory. This program
was written independently for this task. It uses no column-by-column
bitmask DP, external optimization code, published value table, or assumed
formula for the jump set. The expected prefix is used only for comparison
after the optima have been computed.

The minimum soft cost h is the minimum number of omissions; g = k-h
for a prefix of k points. The program accepts an optimum only when the
solver returns SAT and its exact integer objective lower and upper bounds
coincide. The corresponding cover is checked directly against every
generated corner, and its size must equal the objective. UNKNOWN, a
timeout, or unequal bounds aborts; none is interpreted as an optimum.
It also checks that the minimum cover changes by zero or one as each
point is added. Z3's `maxres` engine uses unsatisfiable cores to solve
MaxSAT, avoiding the slow standalone cardinality queries of the initial
small-domain version (commit `a11f93f`).

This is an exact integer/Boolean computation relying on Z3's SAT/UNSAT
optimization answers, not a Lean proof or an independently checked proof certificate.
The program also compares all integer cutoffs through 64 with a separate
exhaustive subset enumeration using the numerical triples n, 2n, 3n.

For reproducible runs with Python 3.10 or later:

```bash
python3 -m venv experiments/.venv
experiments/.venv/bin/python -m pip install -r experiments/requirements.txt
experiments/.venv/bin/python experiments/exact_g.py --limit 288 --output experiments/small-results.json
experiments/.venv/bin/python experiments/exact_g.py --limit 100000000000 --progress --output experiments/results.json
```

The JSON records g at every smooth number, all jumps, minimum-cover
witnesses, and exact rational density bounds. For arbitrary integer t,
g(t) equals the value at the last smooth number at most t, with g(0)=0.
The upper density bound adds all remaining smooth reciprocal terms,
computed exactly as 1 minus one third of the prefix's reciprocal sum.
No floating-point arithmetic is used in optimization or these bounds.

In this environment pip was unavailable. The pinned public PyPI wheel
was downloaded into `/tmp`, its SHA-256 checked, and extracted into a
temporary virtual environment. The wheel digest was
`dfad9e309d7010b1ff6bdb33f21570a1603ef4727373221c7117a74448f0cfef`.
The standard pip instructions above avoid that environment-specific step.
