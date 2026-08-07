# discovery-harness

A **problem-agnostic scientific discovery harness**: an LLM evolves solver
programs (OpenEvolve loop), and a paranoid, *exact* verifier scores every
candidate. The approach follows DeepMind's FunSearch (Nature, 2024) /
AlphaEvolve line of work, rebuilt independently with an emphasis on
**instrument correctness**: no claim is ever made without a certificate
that anyone can re-check in minutes.

Most documentation in this repository is in Turkish (working language);
code, tests, and data formats are self-describing. Start with `CLAUDE.md`
for the full project contract.

## Core principles

- **Verifier asymmetry.** Problems are chosen so that solutions are hard
  to produce but cheap and *exact* to verify (integer / rational
  arithmetic — no floats, no tolerances in the judge).
- **The evaluator never trusts the solver.** Solutions are recomputed
  from raw instances; solver-reported values are ignored (but logged as
  an honesty sensor). Every constraint violation is made unprofitable.
- **Reference values are firewalled.** Known optima / records never reach
  the evolution loop, the instances, or the prompts.
- **Positive and negative controls.** Small cases are proven optimal by
  our own exhaustive enumeration; published certificates (e.g. FunSearch's
  512-point cap set) are re-verified exactly before use as controls.

## Problem tracks

| Track | Problem | Status |
|---|---|---|
| P1 | Multi-type weighted k-out-of-n:G reliability design (target: Ozkut & Tutuncu, C&IE 2025) | Instrument verified against exhaustive ground truth; evolved heuristic reached proven optima on all enumerable instances and closed an n=500 generalization gap (0.652 → 1.000) via a structurally new DP. See `docs/benchmark-v2.md`. |
| P4 | Cap set in F_3^n (the FunSearch problem; open targets: > 236 at n=7, > 512 at n=8) | Instrument validated (FunSearch's published 512-cap re-verified exactly; proven optima for n ≤ 3 by our own B&B). Seed baselines in `docs/p4-baseline.md`. Evolution campaign ready. |
| P2/P3 | MMKP; heterogeneous-fleet VRP with backhauls | Planned. |

Loop mechanics were previously validated on CVRP in a separate repository
(naive seed 44,486 → 33,991; 1.5% gap to best-known).

## Layout

```
harness/    problem-agnostic core: subprocess runner, scoring, plugin registry,
            OpenEvolve evaluator adapter (no problem names in this layer)
problems/   one plugin per problem: parser, exact objective, penalties,
            seed solver, proof-layer enumeration
data/       instances + reference data (provenance in data/*/reference/README.md;
            downloaded third-party sources are not redistributed here)
tests/      positive/negative controls, contract tests, never-raise fuzzing
evolve/     OpenEvolve configs and run scripts
docs/       problem definitions, baselines, benchmark reports (Turkish)
```

## Quickstart

```bash
python -m pytest tests/ -q                 # full test suite
python data/capset/reference/verify_capsets.py   # re-verify reference cap sets
python -m problems.capset.enumerate data/capset/instances/capset-n3.cap  # proven optimum, n<=3
python -m problems.capset.baseline docs/p4-baseline.md                   # seed-vs-known gap table
```

Python 3.14, no external dependencies for the instrument layer;
`openevolve` is required only to run evolution campaigns.

## Honesty guardrails

Reward hacking is treated as the default threat. Fitness (penalized, for
evolution) is kept separate from cost (for claims); "record" claims are
only made for penalty-free, fully feasible solutions re-verified on an
idle machine, against the current published state of the art. Negative
results and instrument bugs are documented, not hidden.

## Contact

Kerem Türkyılmaz — independent researcher.
