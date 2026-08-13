# 4. Case Study Instrument: Covering Designs

## 4.1 Problem and verifier asymmetry

A covering design C(v,k,t) is a collection of k-element blocks from a
v-element universe such that every t-element subset of the universe
is contained in at least one block; the objective is to minimize the
number of blocks. The domain exhibits the *verifier asymmetry* that
guides all our problem choices: constructing good coverings is hard
(the La Jolla repository's upper bounds embody decades of specialized
construction work), but verifying a candidate is exact and cheap —
count, over all C(v,t) t-subsets, whether each is covered. Our
evaluator does exactly this count with integer arithmetic; there is
no floating point anywhere in the scoring path.

## 4.2 Scoring without leakage

Feasible solutions with B blocks score `Schönheim(v,k,t) / B ∈
(0,1]`, where the Schönheim bound — a classical, instance-computable
lower bound — serves as the normalizer. This choice matters for
hygiene: the normalizer injects *no empirical knowledge* (no archive
values, no best-known sizes reach the prompt, the config, or the
scoring function; repository values live in a reference directory
that the loop cannot read). A score of 1.0 means the Schönheim bound
is met, which is rarely possible on large cells; scores are
comparable across cells, enabling multi-instance fitness sets.
Infeasible outputs map into a disjoint band below every feasible
score, graded by the fraction of uncovered t-subsets — an early
timeout that leaves a partial covering still receives gradient.
Format violations (wrong cardinality, out-of-range or duplicate
elements, duplicate blocks) poison the solution but never crash the
evaluator, and work caps guarantee the instrument terminates on
adversarial inputs.

## 4.3 Calibrating the instrument against theory and ground truth

Before any evolution we calibrated the instrument in three layers.
*Curation*: the repository's public data dump was reduced to a
targets table (8,759 cells), validated by hard invariants — the
Schönheim bound never exceeds the recorded lower bound (I1), lower
bounds never exceed recorded sizes (I2), and on the 96 cells with
k = 3, t = 2 the recorded sizes equal the exact Fort–Hedlund value
(T1, 96/96). The same pass surfaced 196 rows of history-hygiene
anomalies in auxiliary fields, fixing the project rule that archive
comparisons always target the `size` field. *Ground truth*: an
exhaustive enumerator (iterative deepening on the block count with
first-uncovered-subset branching and a ⌈uncovered/C(k,t)⌉ bound)
independently re-proved nine archive-proven cells, including
refuting the Schönheim value 11 for C(7,4,3) and certifying 12
(450k search nodes), and proving the gate cell C(13,3,2) = 26 in
milliseconds. These proven cells act as *gates* in every later
experiment: an evolved program failing to reach a proven optimum
signals instrument or population damage before any claim is risked.
*Baseline*: the human-written seed solver (sampled-candidate greedy,
redundancy elimination, ruin-and-recreate; anytime with atomic
output replacement) reaches the proven optima on the gates but sits
far behind the archive on target cells — e.g., 1,269 vs 620 blocks on
C(32,8,4) at small budgets — establishing, via the archive values as
reachability certificates, that genuine headroom exists for evolution
rather than a saturated objective.
