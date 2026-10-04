# Plan for Erdős 168 part ii

The goal is to prove that the limsup of the real sequence F(N)/N is
irrational, without changing the challenge statement. The vendored source
marks this question as open. The user has supplied verified mathematical
facts and exact finite computations, recorded with their scope in NOTES.md.
Stages 1–4 will formalize those facts and the reduction to the jump-set
series. They are not already proved in Lean here. Stage 5 needs an exact
jump rule and a new irrationality argument. No proof code is written here.

## Stage 1: Give the finite maximum a usable interface

- Show that the empty set is admissible, including when N = 0.
- Use `mem_IntervalNonTernarySets_iff` to characterize admissible sets as
  subsets of {1,...,N} containing no entire triple n, 2n, 3n.
- Show that every admissible set has cardinality at most F(N), and that
  an admissible set attaining F(N) exists.
- Prove 0 ≤ F(N) ≤ N, monotonicity, and F(N+1) ≤ F(N)+1 by removing
  the largest element from an optimizer.

These lemmas supply bounds and finite optimizers without unfolding the
powerset in every later argument.

## Stage 2: Split the problem into independent components

Every positive integer has a unique expression q * 2^a * 3^b, where q
is coprime to 6 and a and b are natural numbers.

- Prove existence and uniqueness of this factorization.
- Show that n, 2n, and 3n have the same factor q.
- Identify the component for q inside {1,...,N} with pairs (a,b) satisfying
  2^a * 3^b ≤ floor(N/q).
- Translate a forbidden triple into the three lattice points (a,b),
  (a+1,b), and (a,b+1).
- Prove that the maximum over a disjoint union of these components is
  the sum of their maxima: restrictions give the upper bound, and the
  union of finite optimizers gives the lower bound.

Use g(t) for the maximum cardinality in the lattice component
2^a * 3^b ≤ t. Formalize the verified identity
F(N) = sum over positive q ≤ N coprime to 6 of g(floor(N/q)).
The user checked it against brute force at N = 3, 10, 30, 60, and 100;
the Lean lemma must cover all N independently of those checks.

## Stage 3: Express the maximum using small integer increments

List the distinct numbers of the form 2^a * 3^b in increasing order as
s_0 = 1, s_1 = 2, s_2 = 3, and so on. Put g(0) = 0 and let d_j be
g(s_j) - g(s_j-1). Define J to be the smooth numbers with d_j = 1.

- Prove that this increasing enumeration exists, tends to infinity,
  and has no repetitions.
- Prove that g is constant between consecutive listed numbers.
- Prove d_j is either 0 or 1: adding one point can increase the optimum
  by at most one and cannot decrease it.
- Prove g(t) = sum of d_j over s_j ≤ t, equivalently the number of
  jump points in J at most t. Every positive increment is exactly one;
  some smooth numbers have increment zero.
- Interchange the resulting finite sums to obtain
  F(N) = sum over s_j ≤ N of d_j * C(floor(N/s_j)), where C(x)
  counts positive integers at most x coprime to 6.
- Rewrite the finite expansion as
  F(N) = sum over s in J with s ≤ N of C(floor(N/s)).
- Use the reported jump prefix in NOTES.md and the exact bitmask-DP
  count of 302 jumps among 452 smooth numbers at most 10^11 to guide
  the structural analysis in Stage 5. If computation is extended, record
  its code, recurrence, and results so they can be reproduced. Formalize
  correctness of a DP recurrence only if it is needed by the final proof.

## Stage 4: Prove convergence and identify the limsup

- Count the two allowed residue classes modulo 6 to show
  C(x)/x tends to 1/3, with a uniform bounded counting error.
- Prove convergence of sum_j 1/s_j by rewriting it as
  sum over a,b ≥ 0 of 1/(2^a * 3^b), whose value is 3.
- Bound each normalized summand by 1/s_j, since C(x) ≤ x and d_j ≤ 1.
- For any fixed finite prefix, prove that its contribution to F(N)/N
  tends to (1/3) times the corresponding sum of d_j/s_j.
- Bound the remaining contribution uniformly by the tail of sum_j 1/s_j.
  Combine the finite-prefix limit and tail bound to prove convergence to
  L = (1/3) * sum_j d_j/s_j = (1/3) * sum over s in J of 1/s.
- Use the bounds from Stage 1 and the convergence theorem to identify
  `Filter.atTop.limsup` with L, checking the relevant Mathlib hypotheses.

The reported decimal 0.80096575 is a numerical check, not an irrationality
argument or a certified error bound. This stage will prove limit existence
directly unless a suitable existing proof can be reused. Inspect the public
repository lead in NOTES.md for its actual licence, author credit, revision,
target, and proof dependencies before copying any code. Its licence and
proof status are currently unverified. The vendored `limit_exists` theorem
has an unfinished proof and should not supply evidence for this development.

## Stage 5: Establish irrationality of the specific series

This is the unresolved research stage. The facts d_j ∈ {0,1} and
convergence alone do not imply irrationality. For example, choosing every
d_j = 1 gives the rational sum 3.

- First find and prove an exact rule for membership in J, or an equally
  strong description of the optimizing increments d_j. Seek a recurrence
  or forced patterns from the lattice optimization and reported DP data.
  A finite jump table does not establish the rule beyond its cutoff.
- Study the coefficient-expansion and Diophantine route in the accepted
  Erdős 1062(ii) exposition linked in NOTES.md, crediting its authors.
  That problem has a different divisibility condition, so its component
  formulas and arithmetic conclusions cannot simply be assumed for 168.
- From the proved jump rule, try to regroup the absolutely convergent
  series by powers of two and three into an explicit coefficient
  expansion. Prove the regrouping identity, coefficient bounds, and
  truncation estimates for this problem.
- Determine what rationality of L would force about those coefficients.
  Seek small nonzero linear forms or rational approximants, then prove
  the required Diophantine lower bound with its exact hypotheses. The
  1062 analogy suggests a method; it does not supply this theorem for 168.
- The target separation lemma is: for every integer p and positive
  integer r, sum over s in J of 1/s differs from 3p/r.
- One sufficient alternative would be rational approximants P_k/Q_k to L with
  Q_k positive integers, L different from each approximant, and
  Q_k * |L - P_k/Q_k| tending to zero. Prove these properties from the
  structural theorem before attempting to formalize the contradiction.
- Under L = p/r, distinct rational approximants satisfy
  |L - P_k/Q_k| ≥ 1/(r*Q_k), contradicting that limit.
- If the series does not provide sufficiently strong approximants,
  replace this route with another proved separation argument. Ordinary
  truncations of a convergent series need not meet the required estimate.

Do not treat the separation lemma as a routine missing formalization:
it contains the central open mathematical difficulty. Until it is proved,
this plan does not deliver an irrationality proof.

## Stage 6: Assemble and validate the submission

- Combine the series identity, separation argument, and limsup identity
  to establish the exact target proposition, checking how the configured
  `answer` elaboration affects the equivalence in the source statement.
- Preserve the theorem statement in `tasks/erdos-168-ii/Challenge.lean`.
- Keep the final proof submission free of all forbidden constructs listed
  in AGENTS.md, using the existing submission header for its environment.
- Compile with `lake env lean tasks/erdos-168-ii/Challenge.lean`, and run
  the repository's submission checks when a completed proof exists.
- Update NOTES.md with each result and remaining obstruction, and commit
  each successful step.
