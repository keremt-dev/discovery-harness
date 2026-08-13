# 9. Limitations and Threats to Validity

**Causal claim scope.** The controlled experiment has k = 3 per arm
(the smallest design admitting p ≤ 0.05 on a clean split), one model
family (Claude Opus 5; the engine model was never run with reasoning),
one plateau, one problem. We therefore claim decisiveness of
reasoning mode *in this setting*, not universality; the mixed
ablation literature (Section 2.2) suggests the effect is regime-
dependent, and characterizing that regime is future work.

**Bundled treatment.** Reasoning mode could not be isolated from the
token budget that accommodates it (64k vs 20k); we argue in Section
6.1 that the budget is a constitutive part of the treatment (without
it, reasoning calls return empty content) and note that the disabled
arm never approached its own ceiling.

**Ties, not records.** Every positive result matches a best-known
value; none improves one. The benchmark suggests small stale cells
sit at or near optimality, so tie-density there is informative about
the *method*, not about the frontier. Where real gaps remain (Section
7.4), our artifacts are substantially behind, and we present this
symmetrically.

**Anytime variance and environment.** Evolved solvers are anytime
processes sensitive to machine load. We mitigated with the
work-counter determinism contract and multi-seed fitness, and the
benchmark shows high seed stability (25/29 identical triples), but
runs executed under recorded ambient desktop load (26–41%), not a
dedicated quiet machine; single-seed comparisons inherit a measured
noise band of a few blocks.

**Verification asymmetry of the claim itself.** All quantitative
claims rest on our own instrument. The instrument is calibrated
against theory (Fort–Hedlund exact cells, bound invariants), against
our independent enumerator's proofs, and headline solutions are
re-verified by a standalone stdlib verifier that shares no code with
the harness — but all of these were written within this project; we
release everything for third-party re-verification.

**Contamination residuals.** Section 8 dissociates retrieval from
the reasoning-to-code pathway but cannot prove the absence of
memorized material in model weights; probes ran in single
configurations.

**Engineering external validity.** The ensemble-seeding pathology,
waste dynamics, and proxy-level fixes are reported for one framework
version (OpenEvolve 0.3.2) and one serving stack; they are offered as
cautionary patterns, not as durable properties of those systems.
Candidate processes were not OS-sandboxed on the experiment host.

**Objective vs application.** We optimize the canonical benchmark
objective (minimum block count). Real covering applications carry
side constraints (balance, resolvability, implementation cost) that
our objective does not measure; claims are scoped to the benchmark.
