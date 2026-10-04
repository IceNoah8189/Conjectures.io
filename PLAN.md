# Plan for Erdős 168 part ii

The goal is to prove that the limsup of the real sequence F(N)/N is
irrational, without changing the challenge statement. The vendored source
marks this question as open. This is a research plan, not a completed proof:
Stages 1–4 give a proposed reduction to an explicit convergent series;
Stage 5 needs a new mathematical argument. No proof code is written here.

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

Every positive integer has a unique expression m * 2^a * 3^b, where m
is coprime to 6 and a and b are natural numbers.

- Prove existence and uniqueness of this factorization.
- Show that n, 2n, and 3n have the same factor m.
- Identify the component for m inside {1,...,N} with pairs (a,b) satisfying
  2^a * 3^b ≤ floor(N/m).
- Translate a forbidden triple into the three lattice points (a,b),
  (a+1,b), and (a,b+1).
- Prove that the maximum over a disjoint union of these components is
  the sum of their maxima: restrictions give the upper bound, and the
  union of finite optimizers gives the lower bound.

Define A(t) in the future proof development as the maximum for the single
component consisting of the numbers 2^a * 3^b ≤ t. The resulting identity
should be F(N) = sum over positive m ≤ N coprime to 6 of A(floor(N/m)).

## Stage 3: Express the maximum using small integer increments

List the distinct numbers of the form 2^a * 3^b in increasing order as
s_0 = 1, s_1 = 2, s_2 = 3, and so on. Put A(0) = 0 and let d_j be
the increase in A when the point s_j is added.

- Prove that this increasing enumeration exists, tends to infinity,
  and has no repetitions.
- Prove that A is constant between consecutive listed numbers.
- Prove d_j is either 0 or 1: adding one point can increase the optimum
  by at most one and cannot decrease it.
- Prove A(t) = sum of d_j over s_j ≤ t.
- Interchange the resulting finite sums to obtain
  F(N) = sum over s_j ≤ N of d_j * C(floor(N/s_j)), where C(x)
  counts positive integers at most x coprime to 6.
- Obtain exact finite descriptions or recurrences for A(t) where possible.
  Computed initial values can guide conjectures, but are not a substitute
  for a structural theorem about the whole sequence d_j.

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
  L = (1/3) * sum_j d_j/s_j.
- Use the bounds from Stage 1 and the convergence theorem to identify
  `Filter.atTop.limsup` with L, checking the relevant Mathlib hypotheses.

This stage should prove limit existence directly. The vendored
`limit_exists` theorem has an unfinished proof and should not supply
mathematical evidence for this development.

## Stage 5: Establish irrationality of the specific series

This is the unresolved research stage. The facts d_j ∈ {0,1} and
convergence alone do not imply irrationality. For example, choosing every
d_j = 1 gives the rational sum 3.

- First prove a structural theorem about the actual optimizing increments
  d_j. A recurrence, forced patterns, or quantitative information about
  their tails would be candidates; none has been established here.
- Seek an arithmetic separation lemma: for every integer p and positive
  integer q, show sum_j d_j/s_j differs from 3p/q.
- One sufficient route would be rational approximants P_k/Q_k to L with
  Q_k positive integers, L different from each approximant, and
  Q_k * |L - P_k/Q_k| tending to zero. Prove these properties from the
  structural theorem before attempting to formalize the contradiction.
- Under L = p/q, distinct rational approximants satisfy
  |L - P_k/Q_k| ≥ 1/(q*Q_k), contradicting that limit.
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
