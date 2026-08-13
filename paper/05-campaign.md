# 5. The Evolution Campaign

This section narrates the C(32,8,4) marathon chronologically, because
the sequence itself — fast early gains, a genuine plateau, a failed
conventional escalation, and a reasoning-mode breakthrough — is the
experimental substrate for Section 6. [Fig. 2: best-score timeline
across slices.] An earlier week of the same campaign, using
pre-breakthrough artifacts and focused single-cell slices, had
already matched five other decades-old repository values (including
C(28,9,3) = 56, three independent certificates); we reference those
results as context but the present narrative concerns the marathon
cell C(32,8,4), whose archive value (620, dated 1996) stood 396
blocks below our best artifact at the campaign's start.

## 5.1 Setup and early gains

The marathon configuration follows an AlphaEvolve-style two-model
ensemble — a cost-efficient engine model (GLM-5, weight 0.8) and a
flagship (Claude Opus 5, weight 0.2), both mutating via
search-replace diffs — over a single-cell fitness set with two-seed
mean fitness and a 300 s solver budget (Section 3.2). Two
pre-launch measurements shaped the design. First, the strongest
prior artifact silently capped its internal time budget at 50 s; with
the cap lifted, six times more wall-clock *alone* did not improve
quality (1,016 vs 1,013 blocks) — wall-clock-fraction phase budgets do
not scale, so the additional budget had to be made exploitable by
evolution. Second, a five-iteration smoke run immediately improved
the two-seed score from 0.5181 to 0.5423 (978 blocks, later
re-measured at 977), beating the previous all-time artifact within
five mutations and validating the ensemble plumbing end-to-end.

## 5.2 The plateau, instrumented

The next 50 ensemble iterations produced *zero* improvements — but
attributing this to a search plateau required first eliminating an
instrumentation artifact. In the first 25-iteration slice, 48% of
LLM calls were wasted: 36% produced children exceeding the harness's
maximum program length (the genome had grown to ~30k characters, so
additive diffs pierced the 35k cap), and 12% were unparseable diffs.
Raising the cap to 45k and adding an explicit pruning instruction to
the mutation contract ("prefer replacing code over accumulating it")
cut waste to 8% in the second slice — which still yielded zero
improvements. The conventional escalation, a 25-iteration
full-rewrite slice with the reasoning-disabled flagship (the exact
recipe that had broken an earlier plateau on C(28,9,3)), also failed:
24/25 valid rewrites, of which four independently returned to
*exactly* 0.5423/977 and the rest clustered in 977–980. At this
point the plateau was real and instrument-clean: 75 iterations, three
configurations, one attractor.

A software finding from this phase is worth reporting for users of
similar frameworks: the evolution framework seeds each worker
process's model-selection RNG identically, so every worker draws the
same model sequence — in short runs the configured 0.8/0.2 ensemble
mix collapses (our five-iteration smoke run sent 5/5 calls to the
20%-weight model; we verified the effect end-to-end via proxy request
logs and reproduced the draw sequence analytically). Over long runs
the mix converges to the configured weights (21.3% over each worker's
75-draw prefix), but short diagnostic slices systematically
misrepresent ensemble behavior.

## 5.3 The breakthrough and what was discovered

The reasoning-enabled slice that followed (motivation and controls in
Section 6) broke the plateau in its first improving iteration:
combined score 0.5423 → 0.8581, cost 977 → 620, matching the archive
value to the block. The discovered program deserves description.
[Fig. 3: the `affine_blocks` routine as evolved.] The new routine
detects whether v = pᵐ for a small prime p; if so it constructs the
translation group of the affine geometry AG(m,p) by digit-wise
addition modulo p, enumerates all d-dimensional linear subspaces by
repeated closure — d chosen maximal with pᵈ ≤ k — and emits every
coset (d-flat) as a block, padding blocks with random extra points
when k > pᵈ. For (v,k,t) = (32,8,4): p = 2, m = 5, d = 3, giving all
3-flats of AG(5,2). Correctness is structural — any 4 points span an
affine subspace of dimension ≤ 3 and hence lie in some 3-flat — and
the count is exact: 2^{m-d} · [m choose d]_p = 4 · 155 = 620 blocks.
This is a classical construction; the 1996 archive value almost
certainly descends from the same family (Gordon, Kuperberg, and
Patashnik's founding paper for the repository explicitly searched
AG(m,p) flats). Three properties matter for our claims: the code
contains *no* stored blocks or table values (its only dense numeric
literal is a list of small primes); it is *general*, deriving the
construction for any prime-power universe, which Section 7 exploits;
and it was produced under a loop that never saw the number 620 in
any input. The solution was captured by the archiving hook in
triplicate, re-verified by the standalone verifier (35,960 of 35,960
t-subsets covered), and cross-checked against the live successor of
the frozen repository on the same day.

## 5.4 Cost accounting

For reproducibility budgeting: the marathon consumed approximately
115 engine-model calls (diff mode, ~3.4k output tokens each), 85
reasoning-disabled flagship calls (full rewrites, 7–9k tokens), and
40 reasoning-enabled flagship calls (~48k output tokens each,
dominated by reasoning traces), plus roughly 60 CPU-hours of
evaluation. The entire discovery phase — from campaign start to the
verified 620 — fit in under three days of wall-clock time on one
desktop machine.
