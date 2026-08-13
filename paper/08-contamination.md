# 8. Contamination Analysis

The obvious objection to any rediscovery claim is that the model
memorized the answer: repository tables and the founding
constructions paper are public and almost certainly in the training
corpus. We address the objection with six audit lines and a
dissociation experiment, and we calibrate the claim accordingly.

**Audit lines.** (K1) The winning program contains no stored blocks,
sizes, or cell-specific constants — its only dense numeric literal is
a list of small primes; the construction is *derived* for arbitrary
prime-power universes. (K2) No archive value ever entered the loop's
inputs: prompts and configurations are grep-audited per commit, and
the value 620 appears in no artifact the LLM could read. (K3) In
C(49,8,2) the pure construction yields 56 blocks while the tie
requires 49; the gap was closed by the evolved local search —
behavior a lookup cannot produce. (K4) Four benchmark ties occur in
cells where the affine construction is inapplicable, including one
value (C(23,10,3) = 24) that no earlier artifact of the campaign had
reached. (K5) Retrieval is cheap and does not require reasoning
tokens; yet the identical model failed 55/55 full-rewrite attempts
with reasoning disabled and succeeded 3/3 with it enabled. A
memorization mechanism would appear in both arms. (K6) Every claimed
artifact is verified by exact recount; contamination could at most
affect the interpretation (discovery vs rediscovery) — and we claim
only rediscovery.

**Dissociation probes.** We probed the deployed model directly
(temperature 0). Asked for the best-known value of C(32,8,4), the
reasoning-disabled model *declined to produce a number*, stating it
did not reliably know it. Asked to emit an explicit covering as plain
text — no code allowed — the reasoning-enabled model consumed its
entire 64k-token budget in reasoning (596 s) and emitted *zero
blocks*. The same model, allowed to write code inside the loop,
produced a correct general construction in every enabled repeat.

**Table 3 — Capability dissociation.**

| Capability | Probe | Outcome |
|---|---|---|
| Recall the value 620 | direct question, temp 0 | unreliable (declined) |
| Emit the artifact directly | 64k-token reasoning, no code | failed (0 blocks) |
| Select paradigm and implement as code | evolution loop (Sec. 6) | reliable (3/3) |

**Calibrated claim.** The model's latent mathematical knowledge —
that affine geometries yield good coverings is textbook material — is
a *permitted resource*, exactly as a human expert's literature
knowledge would be. What the experiments show is that this knowledge
is not accessible as retrieval: it becomes a verified artifact only
through the reasoning-to-code-to-execution pathway that the harness
provides and the reasoning mode unlocks. We do not claim the
knowledge is absent from the weights (a null probe cannot prove
absence, and the probes ran in single configurations); we claim, and
demonstrate, that the pipeline — not recall — is what produces the
verified object.
