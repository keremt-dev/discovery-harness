# 3. The Discovery Harness

Our harness descends from the FunSearch/AlphaEvolve template — an LLM
proposes program mutations, an evaluator scores them, an evolutionary
database (MAP-Elites over islands; we use OpenEvolve) maintains the
population — but its design center is different: *every scored value
is recomputed by a mathematically exact instrument, and nothing the
evolved program says about itself is trusted.* This section describes
the contract that enforces this, and the design decisions that were
each paid for by a concrete failure earlier in the project.

## 3.1 Problem plugins and the exactness contract

The core (`harness/`) never mentions any concrete problem. A problem
is a plugin exposing four members: a `SENSE` flag ("min"/"max"), a
strict instance parser, an evaluator `evaluate_text(instance, text) →
verdict`, and a penalty scale derived from the instance. Two
asymmetric error policies apply: a malformed *instance* raises
immediately (instrument fault — the loop must halt), while a
malformed *solution* never raises — it produces a graded, penalized
verdict, because candidate programs will emit garbage and the loop
must keep moving. The verdict separates `fitness` (penalized, for
evolution) from `cost` (the claim-bearing objective, defined only for
feasible solutions); conflating the two is a classic reward-hacking
door and is structurally closed here. The sign convention between
`SENSE` and the maximizing evolution engine is applied in exactly one
function — an inverted sign silently reverses evolution, so this
conversion is the most heavily unit-tested line of the codebase.

Evolved programs run in a separate process with a temporary working
directory and a wall-clock kill; whatever partial output exists at
timeout is rescued and graded (all our solvers are anytime by
contract). The evaluator recounts everything from the raw instance
with exact arithmetic — exact rational arithmetic (`Fraction`) for
the reliability case study, exact integer counting for covering. A
solver's self-reported objective is ignored, but *whether it matches*
the recount is logged as a silent honesty sensor. Penalty scales are
derived from instance data such that no constraint violation can ever
be profitable; the test suite asserts the invariant "every infeasible
verdict scores strictly below every feasible one" per plugin.

## 3.2 Multi-seed fitness and the determinism contract

Two additions were forced by a painful incident. In an earlier
record-hunting run on C(28,9,3), a 56-block solution was observed
once by the evaluator, was not persisted, and could not be reproduced
afterwards: the genome derived internal phase budgets from wall-clock
fractions, so even fixed-seed reruns diverged under machine-load
variation (measured same-seed spread on that genome: 63–73 blocks).
The episode produced three mechanisms. First, *solution archiving*:
an environment-gated hook persists every feasible solution passing a
cost threshold to durable storage under a content-hashed filename
(idempotent under parallel evaluation, never able to raise into the
evaluation path). Second, *multi-seed fitness*: the adapter can run a
candidate once per seed in a declared list, passing `--seed N` on the
CLI; the evolutionary fitness is the *mean* of combined scores over
seeds, the reported cost is the best run's. A program that is only
occasionally lucky is thereby scored as such — fitness measures the
program, not one machine-moment. Third, a *determinism contract* in
the mutation prompt: internal phase budgets must be derived from work
counters (iterations, node counts), never from wall-clock fractions,
with wall-clock permitted only as the final hard stop. Section 7's
seed-stability result (identical costs across three seeds in 25 of 29
cells) is the empirical yield of this contract.

## 3.3 Problem-agnosticism as a tested property

The harness's generality is not aspirational but regression-tested:
after the initial reliability-design case study (weighted k-out-of-n
systems, where small instances have *provably* optimal solutions via
exhaustive enumeration, giving the evaluator itself a measurable
accuracy), a cap-set plugin (the FunSearch precedent problem) and the
covering-design plugin of this paper were each added with zero
changes to the core — the project treats any needed core edit as a
leak to be fixed, not accommodated. We disclose one accepted
limitation: on the Windows host used for these experiments, the
candidate subprocess is not OS-sandboxed (no network/memory isolation
enforcement); the risk is accepted for a single-user machine and the
setup is portable to containerized execution.
