# 2. Related Work

## 2.1 LLM-driven evolutionary program search

FunSearch [Romera-Paredes et al. 2024] established that pairing an
LLM mutation operator with a programmatic evaluator can produce new
mathematical constructions (cap sets, bin-packing heuristics).
AlphaEvolve [Novikov et al. 2025] generalized the recipe to whole
codebases and reported results across more than fifty mathematical
problems — rediscovering the best known construction in ~75% of them
and improving it in ~20%, a framing that makes *rediscovery rate* an
accepted currency of this literature and one we adopt. Follow-on
systems refine the search architecture: ShinkaEvolve [Sakana AI 2025]
targets sample efficiency (circle packing, Heilbronn triangles,
autocorrelation inequalities), CodeEvolve [2025] provides an open
implementation, and Nagda et al. apply reinforced variants to Ramsey
and Zarankiewicz numbers, explicitly reporting recovery of known
bounds alongside improvements. Negative results have also begun to
appear (bijection discovery with OpenEvolve remaining hard), which we
take as a healthy norm and follow in Sections 7.4 and 9. Analyses of
*why* these loops work concentrate on the evolutionary component
[PPSN 2024]; the contribution of specific *model capabilities* —
in particular extended reasoning — has, to our knowledge, not been
isolated experimentally in a discovery loop. Across all published
problem lists of this lineage we find no covering-design instances;
both gaps are addressed here.

## 2.2 Reasoning-mode ablations

Controlled comparisons of LLMs with reasoning enabled versus disabled
exist outside discovery loops, with strikingly mixed outcomes:
reasoning helps handwriting-synthesis agents and long-form
information-control tasks, is neutral for prompt-attack detection,
and *degrades* content-moderation accuracy. This task-dependence is
the backdrop against which our result should be read: in the
structural-paradigm-shift regime of Section 6, the effect is not a
few points of accuracy but a categorical 3/3-versus-0/3 separation
with a 36% objective improvement.

## 2.3 Covering designs

Upper bounds for covering numbers C(v,k,t) are curated by the La
Jolla Covering Repository and its live successor. The founding
constructions paper [Gordon, Kuperberg & Patashnik 1995] combined
greedy methods, finite-geometry constructions (including AG(m,p)
flats — the family our loop rediscovers), and synthesis rules;
subsequent stochastic-search work (simulated annealing [Nurmela &
Östergård 1993+], cooperative tabu search [2006]) improved many small
cells. The specific cells we target have been stable for 15–30
years, and we find no post-2020 method wave touching them — a
stagnant-frontier setting that makes exact ties informative even
though they set no records.
