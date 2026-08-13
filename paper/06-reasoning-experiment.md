# 6. Controlled Experiment: Reasoning Mode as the Plateau Breaker

## 6.1 Motivation and design

The campaign of Section 5 left the population in a stable plateau:
after 75 iterations (50 ensemble iterations followed by 25 full-rewrite
iterations with the reasoning-disabled flagship model), the best
program scored 0.5423 (977 blocks) and independently generated
children clustered tightly in the 977–980 band. A single subsequent
slice with the *same* flagship model but with extended reasoning
enabled broke the plateau in its first improving iteration, producing
a general affine-geometry construction that reaches exactly 620
blocks — the best-known value for C(32,8,4) since 1996. One
observation, however, cannot distinguish a causal effect of reasoning
mode from a lucky draw. We therefore ran a controlled repetition
experiment.

**Design.** Both arms resume from the same frozen evolution state
(checkpoint after iteration 75; best program 0.5423/977, population of
39 programs across 4 islands). Each arm runs k = 3 independent slices
of 10 iterations each. The arms are paired by the evolution RNG seed
(43, 44, 45 for repeats 1–3 in both arms) and executed in alternating
order (ON-r1, OFF-r1, ON-r2, ...) so that machine-load drift affects
both arms symmetrically. Everything else is held fixed: the same
model (Claude Opus 5 via a local OpenAI-compatible proxy), the same
system message, full-rewrite mutation mode in both arms, temperature
0.8, and the same evaluation pipeline (fitness = mean combined score
over two solver seeds, 300 s solver budget per run, hard kill at
320 s).

**Treatment definition.** The treatment is "extended reasoning with a
token budget that accommodates it". The reasoning-enabled arm runs
with max_tokens = 64,000 and a 900 s request timeout, because measured
reasoning traces consume ≈42k tokens before content emission; the
reasoning-disabled arm retains the campaign configuration
(max_tokens = 20,000, 600 s timeout). We disclose this as a bundled
confound rather than attempt to equalize budgets: a reasoning call
*requires* the larger budget (at 20k tokens the reasoning path
produces empty content, Section 5), while the disabled arm never
approached its 20k ceiling (zero truncation events across all
disabled-arm calls; typical completions of 7–9k tokens). The
effective budget available for *content* is therefore comparable
across arms; the additional tokens in the enabled arm are consumed by
reasoning itself.

## 6.2 Results

Table 1 summarizes the six slices. We define a *breakthrough* as any
child whose verified cost falls below 900 blocks (the plateau band
never left 977–1011; the observed breakthroughs all reach 620, so the
threshold is not sensitive).

**Table 1 — Reasoning-mode experiment (10-iteration slices from the
frozen plateau state).**

| Slice | Reasoning | RNG seed | Valid iters | First improvement (slice iter) | Best score | Best cost | Breakthrough |
|---|---|---|---|---|---|---|---|
| ON-r1 | enabled | 43 | 10/10 | 8 | 0.8581 | **620** | yes |
| ON-r2 | enabled | 44 | 10/10 | 4 | 0.8581 | **620** | yes |
| ON-r3 | enabled | 45 | 10/10 | 3 | 0.8581 | **620** | yes |
| OFF-r1 | disabled | 43 | 10/10 | 2 (jitter: +0.0003, 978 blocks) | 0.5426 | 978 | no |
| OFF-r2 | disabled | 44 | 10/10 | — | 0.5423 | 977 | no |
| OFF-r3 | disabled | 45 | 10/10 | — | 0.5423 | 977 | no |

Every reasoning-enabled slice broke the plateau, and each reached
*exactly* 620 blocks — the affine construction re-emerged
independently in all three repeats, from different parents and
different LLM samples. No reasoning-disabled slice produced anything
outside the plateau band; the only nominal "new best" in that arm was
a +0.0003 score jitter at unchanged solution quality. The
disabled-arm children over all three slices (plus the 25 disabled
full-rewrite iterations of Section 5, which used the same
configuration from an earlier checkpoint) span 55 full-rewrite
attempts without a single structural jump.

One procedural incident is disclosed for completeness: the first
execution of OFF-r3 was invalidated by provider-side rate limiting
(48 HTTP-429 responses; only 2 of 10 iterations completed, neither
improving). The slice was re-run under the identical configuration
once quota recovered; the re-run (10/10 valid iterations, no
breakthrough) is the observation reported in Table 1.

## 6.3 Statistical analysis

Under the null hypothesis that reasoning mode does not affect
breakthrough probability, the observed split (3/3 vs 0/3) has
one-sided Fisher exact probability p = 1/C(6,3) = 0.05. Two
supporting observations lie outside the pre-registered design: the
original discovery slice (reasoning-enabled, breakthrough to 620;
including it gives 4/4 vs 0/3, p = 1/35 ≈ 0.029) and the 25
reasoning-disabled full-rewrite iterations of Section 5 (0
breakthroughs). The effect size is not marginal: every success
reduced the best-known-to-us cost by 357 blocks (36%), from the
plateau at 977 to the 30-year-old best-known value.

We emphasize the scope of the claim: this experiment establishes that
extended reasoning was decisive *for this model, on this plateau, in
this loop* — a structural-paradigm-shift setting. It does not claim
that reasoning helps uniformly; published ablations in other task
families report mixed and even negative effects (Section 2), which
makes the categorical separation observed here noteworthy.

## 6.4 Cost analysis and a practical recipe

Reasoning calls are expensive: measured completions consumed ≈47.7k
output tokens per call (of which ≈42k reasoning) versus 7–9k for
disabled-arm calls — roughly a five-fold output-token cost, with
~9–10 minute latency per call. The experiment thus supports a
two-tier operating recipe for LLM-evolutionary search, echoing but
sharpening the fast/strong model split of AlphaEvolve: run routine
incremental evolution with cheap non-reasoning calls, and spend
reasoning-enabled calls *only when the population plateaus and the
problem plausibly demands a change of construction paradigm*. In our
campaign this recipe would have saved the entire 25-iteration
non-reasoning full-rewrite slice, whose 55 attempts explored the
plateau's basin without ever leaving it.
