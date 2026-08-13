# TELO Cover Letter (ScholarOne'daki "Cover Letter" alanına yapıştırılacak)

Dear Editors,

Please consider our manuscript "Reasoning Mode Breaks the Plateau:
Verified LLM-Evolutionary Search Matches Three Decades of Best-Known
Covering Designs" for publication in ACM Transactions on Evolutionary
Learning and Optimization.

The paper makes four contributions at the intersection of LLM-driven
program evolution and combinatorial construction. (1) It reports, to
our knowledge, the first controlled experiment isolating the effect of
a model's extended reasoning mode inside an evolutionary discovery
loop: from a frozen plateau state, reasoning-enabled slices broke the
plateau 3/3 times — each independently rediscovering the classical
affine-geometry construction and matching the 30-year-old best-known
value C(32,8,4) = 620 — while reasoning-disabled slices with the same
model failed 0/3. (2) Under a benchmark protocol frozen before
execution, the single evolved program matched 22 of 29 best-known
covering repository values, including four in cells outside its
discovered construction family, with every tie re-verified by a
standalone verifier. (3) The problem-agnostic harness design
(exactness-first evaluation, multi-seed fitness, work-counter
determinism, solution archiving) and its documented failure-driven
rationale are reported for reuse, together with negative results.
(4) A contamination analysis dissociates memorization from the
reasoning-to-code pathway via direct-recall probes.

All positive results are ties with best-known values, not records;
the paper is explicit about this framing throughout. All code,
certificates, frozen protocols, and raw logs are publicly available
(github.com/keremt-dev/discovery-harness; archived at
doi:10.5281/zenodo.21920942), in line with TELO's reproducibility
emphasis. The pre-registration of the benchmark protocol is
verifiable from the repository's commit timestamps.

This manuscript is not under consideration elsewhere. [ArXiv ön-baskı
yayınlanırsa şu cümle eklenecek: "A preprint is available as
arXiv:XXXX.XXXXX."] The author declares no conflicts of interest.

Sincerely,
Kerem Türkyılmaz
Independent Researcher
ORCID: 0009-0008-1447-9768
