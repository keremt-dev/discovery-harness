You are evolving `solver.py`, a single-file Python solver for the
**cap set** problem in the vector space F_3^n (find the largest subset
S of {0,1,2}^n such that no three DISTINCT vectors x, y, z in S satisfy
x + y + z = 0 mod 3, componentwise — equivalently, no 3-term arithmetic
progression and no affine line).

Contract — breaking any of these gets a heavily penalized score:
- CLI: python solver.py <instance.cap> <output.txt>
- Input: line-based text; '#' starts a comment. The only header is
  `dimension <n>` (an integer >= 1). That single number n defines the
  space {0,1,2}^n; there are 3^n candidate vectors total.
- Output: zero or more lines, each EXACTLY n characters from {0,1,2},
  written contiguously (e.g. for n=8 a line looks `02110221`). Each line
  is one vector you choose to include in S. Lines starting with '#' are
  comments and are ignored. You MAY write a line `# size <int>` with
  your own size estimate — it is IGNORED for scoring (the evaluator
  recomputes |S| exactly) but logged as an honesty sensor.
- The order of output lines does not matter. Duplicate vectors are a
  VIOLATION (duplicate_vector), not silently de-duplicated — every line
  must be a distinct vector. A line of the wrong length, or containing
  any character other than 0/1/2, is a violation (bad_vector).
- Feasibility (cap-set property): for every pair {x, y} of DISTINCT
  chosen vectors, the third vector z = -(x+y) mod 3 (componentwise) must
  NOT be in S. If any such z is present (and distinct from x, y), the
  whole solution is infeasible (line_found) and scores far below any
  feasible set — even the empty set. Protect feasibility first.
- Determinism: same input must produce same output (fixed seeds only).
- Resources: single process, ~50 seconds wall clock (the runner kills at
  55 s), CPU only. Python stdlib and numpy are available. No network,
  no threads needed, no file access other than the two argv paths.

ANYTIME IS MANDATORY. Write your output incrementally and atomically:
maintain a `.tmp` file and replace the real output with `os.replace`
whenever you find an improved feasible set. The runner may kill you at
the 55 s wall clock; if you only write at the very end, a timeout yields
an empty solution (score 0). Write your first feasible set within the
first 1-2 seconds, then keep improving. Partial/corrupt lines must never
appear in the output file — only ever replace a valid file with another
valid file.

Goal: MAXIMIZE |S|, the number of vectors in your cap set. The evaluator
checks the cap-set property with exact integer arithmetic (no floats, no
tolerance): for each pair it computes z = -(x+y) mod 3 and tests set
membership. This is O(|S|^2) and cheap; you should verify your own
candidate with the same rule before writing it.

Promising directions:
- A greedy construction: consider vectors in some priority order; add a
  vector if it does not complete a line with any two already-chosen
  vectors (maintain the set of vectors that would now be "blocked"). The
  priority function is the lever to evolve — symmetries, weight (number
  of nonzero entries), and reflection structure matter.
- After construction, extend: any vector not yet blocked can still be
  added. Then local search: remove one vector, which un-blocks some
  region, and try to add two or more in its place (1-for-k swaps).
- Random restarts within the time budget; keep the best set found.
- The space has rich algebraic structure (lines, hyperplanes, products);
  constructions exploiting it can be much larger than naive greedy.
  Discover such structure — do NOT hardcode specific known large sets.

SCALE: the score is the MEAN fitness over all instances in the set
(typically dimension 7 and 8, plus a smaller "watch" instance). Your
solver must produce valid, large cap sets across dimensions. A single
infeasible or empty output on any instance drags the mean down hard, so
robustness across n matters as much as peak size on one n.
