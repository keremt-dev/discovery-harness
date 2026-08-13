# Abstract (final)

LLM-driven evolutionary program search has produced striking
mathematical constructions, but the literature says little about
*which model capability does the breakthrough work*. We study this
question on covering designs C(v,k,t) — a classical construction
domain untouched by the FunSearch/AlphaEvolve lineage — using a
problem-agnostic evolution harness whose defining property is that
every score is recomputed by a mathematically exact verifier and no
claim rests on model or solver self-report. Starting from a generic
greedy solver, our campaign improved C(32,8,4) from 1,258 to 977
blocks and then stalled: across 75 iterations and three
configurations, including full rewrites by the flagship model with
reasoning disabled, no mutation left the plateau. With extended
reasoning enabled — and nothing else changed — the same model broke
the plateau in its first improving iteration by writing a *general*
affine-geometry construction, matching the best-known value of 620
blocks, unimproved since 1996. A controlled repetition from the
frozen plateau state separates the arms categorically: reasoning-on
3/3 breakthroughs, each independently reaching exactly 620;
reasoning-off 0/3 (one-sided p = 0.05; effect −36%). Under a
pre-registered 29-cell benchmark the single evolved program matched
22 best-known values — including four in cells where its discovered
construction is inapplicable — with every tie re-verified by an
independent verifier and high cross-seed stability (25/29 identical
triples). Direct-recall probes show the model can neither state the
target value nor emit the artifact without writing code, dissociating
memorization from the reasoning-to-code pathway. We release all
certificates, frozen protocols, raw logs, and negative results.

# 1. Introduction

In late 2023, FunSearch demonstrated that a large language model
inside an evolutionary loop can produce genuinely new mathematics;
AlphaEvolve scaled the recipe to dozens of problems and whole
codebases. These systems are typically reported as monoliths: a
model, a mutation scheme, an evaluator, a database — and a result.
When the result is good, it is hard to say which ingredient earned
it. Practitioners inherit an expensive ambiguity: should the next
budget go to more iterations, a bigger population, a stronger model —
or to a different *mode* of the same model?

This paper isolates one ingredient experimentally: the model's
extended reasoning mode ("thinking"), in which the model produces a
long private chain of thought before its answer. Our vehicle is a
campaign on covering designs — minimum collections of k-element
blocks covering all t-subsets of a v-element universe — chosen for
three properties. First, *verifier asymmetry*: constructing good
coverings has occupied specialists for decades, but verifying a
candidate is exact integer counting, which suits our harness's
governing rule that nothing an evolved program says about itself is
ever trusted. Second, the domain has a canonical, curated frontier
(the La Jolla Covering Repository and its live successor) whose
values on our target cells have stood for 15–30 years — a stagnant
frontier against which even exact ties are informative. Third, to
our knowledge no system in the FunSearch lineage has touched it.

The campaign itself furnished the experiment. Cheap ensemble
evolution improved C(32,8,4) from a 1,258-block seed baseline to 977
blocks within five mutations, then plateaued. We spent 75 iterations
establishing that the plateau was real rather than an instrument
artifact: we repaired a mutation-waste pathology (48% of calls were
being rejected before evaluation), verified the fix (waste fell to
8%), and escalated to the conventional remedy — full rewrites by the
flagship model — which produced children clustering to the *exact*
plateau value from four independent rewrites. Then we enabled
extended reasoning on the same model, same prompt, same frozen
population. The first improving iteration rewrote the solver around
a general finite-geometry construction — all d-flats of AG(m,p) for
any prime-power universe — whose block count at (32,8,4) is exactly
620: the repository's best-known value, dated 1996, and 357 blocks
(36%) below the plateau. A controlled repetition experiment from the
frozen state confirmed the effect is categorical, not luck: three of
three reasoning-enabled slices rediscovered the construction
independently; zero of three reasoning-disabled slices left the
plateau band (p = 0.05, one-sided Fisher; 55 disabled full-rewrite
attempts in total never produced a structural change).

We then asked what the discovery is worth beyond its cell. Under a
benchmark protocol frozen before execution — 29 cells spanning
proven-optimum gates, affine-family holdouts, and cells where the
affine construction cannot apply — the single evolved program matched
the best-known value in 22 cells with zero per-cell adaptation,
including C(49,8,2), where the pure construction is seven blocks
short and the evolved local search closes the gap, and four
non-prime-power cells served purely by the evolved search machinery.
All ties were re-verified by a standalone verifier sharing no code
with the harness. Because "the model memorized the tables" is the
natural objection, we also ran dissociation probes: the deployed
model, asked directly, declines to state the value of C(32,8,4); and
asked to emit a covering as plain text with a 64k-token reasoning
budget but no code, it produces zero blocks. The capability that
matters is not recall but the reasoning-to-code-to-execution pathway.

Our contributions:

**C1 — A controlled reasoning-mode experiment in an evolutionary
discovery loop** (Section 6): to our knowledge the first, showing a
categorical 3/3-vs-0/3 breakthrough separation with a 36% objective
effect, against a backdrop of mixed reasoning-ablation results in
other task families.

**C2 — Verified rediscovery at a stagnant frontier** (Sections 5, 7):
22 of 29 pre-registered cells tied to best-known values by one
evolved program, every tie independently verified; covering designs
enter the LLM-evolutionary literature.

**C3 — An exactness-first, problem-agnostic harness** (Sections 3-4):
plugin contract with fitness/cost separation, multi-seed fitness,
work-counter determinism, solution archiving, and leak-audited
prompts — each mechanism motivated by a documented failure; plus
engineering findings (mutation-waste dynamics, an ensemble-seeding
pathology) reported for reuse.

**C4 — A contamination-dissociation methodology** (Section 8):
value-recall, direct-artifact, and code-pathway probes that calibrate
what "rediscovery" means when the literature is in the weights.

Sections 2 reviews related work; Section 9 details limitations —
foremost that all positive results are ties, not records, and that
the causal claim is scoped to one model, one plateau, one domain.
Everything needed to re-verify or extend this work — harness,
certificates, protocols, raw logs — is released as open source.
