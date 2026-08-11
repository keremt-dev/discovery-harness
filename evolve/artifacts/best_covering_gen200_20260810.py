"""Covering design solver C(v,k,t): minimize blocks covering all t-subsets.

Pipeline
--------
0. Dense t-subset indexing: every t-subset of {0..v-1} -> integer id.
   Per-block id lists and per-(rest,elem) id lists are memoised, so all
   coverage bookkeeping is plain integer list arithmetic.

A. Exact max-gain greedy (no candidate sampling) => a complete covering
   is on disk within the first seconds (anytime milestone #1).

B. Orbit-greedy cyclic skeleton: under x -> x + s (mod v) each base block
   spans an orbit of <= v blocks.  We greedily stack the orbit with the
   best (new coverage / orbit size) ratio -- so a 400-block covering is
   assembled from ~20 base blocks, not 2-3 -- and patch the residue with
   the greedy.  This is the structural lever.

C. Redundancy removal to a fixed point.

D. MAIN LEVER: fixed-size local search at b = |best| - 1 blocks.  Minimize
   the number of uncovered t-subsets with single-element swaps guided by a
   random uncovered t-subset, with tabu memory and plateau kicks.  The
   search state is PERSISTENT across time slices at a given target size so
   effort accumulates.  Cost 0 => a strictly smaller covering.

E. Ruin-and-recreate diversification when D stalls.

Every improvement is written atomically (os.replace).  Deterministic.

CLI: python solver.py <instance.cover> <output.txt> [--seed N]
Env: COVERING_SEED_TIME_S (default 10).
"""

import argparse
import os
import random
import time
from itertools import combinations

# ------------------------------ tunables -----------------------------
ORBIT_FRAC = 0.22         # budget share for the orbit-greedy skeleton
ORBIT_CAND = 24           # candidate bases scored per orbit pick
ORBIT_ROUNDS = 4
RESTART_FRAC = 0.10       # budget share for diversified greedy restarts
TABU_FRAC = 0.11
RUIN_MAX = 4
SLICE_FRAC = 0.55         # share of remaining time per fixed-size attempt


# ---------------------------- instance I/O ---------------------------
def parse_instance_file(path):
    vals = {}
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            key = parts[0].lower()
            if key in ("v", "k", "t") and len(parts) >= 2:
                vals[key] = int(parts[1])
    if set(vals) != {"v", "k", "t"}:
        raise ValueError("v/k/t headers missing")
    return vals["v"], vals["k"], vals["t"]


def format_solution(blocks):
    out = [f"# size {len(blocks)}"]
    for b in blocks:
        out.append(" ".join(str(x) for x in b))
    return "\n".join(out) + "\n"


def _atomic_write(path, text):
    tmp = str(path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, str(path))


# --------------------- t-subset indexing structure -------------------
class TIndex:
    """Dense id for every t-subset of {0..v-1}, plus memoised caches."""

    def __init__(self, v, t):
        self.v = v
        self.t = t
        self.tsets = list(combinations(range(v), t))
        self.n = len(self.tsets)
        self.idx = {ts: i for i, ts in enumerate(self.tsets)}
        self._bcache = {}
        self._wcache = {}

    def block_ids(self, block):
        """Ids of all t-subsets inside `block` (a sorted tuple)."""
        got = self._bcache.get(block)
        if got is None:
            ix = self.idx
            got = [ix[c] for c in combinations(block, self.t)]
            if len(self._bcache) < 300000:
                self._bcache[block] = got
        return got

    def ids_with(self, rest, e):
        """t-subsets = {e} + (t-1) elements from the sorted tuple `rest`."""
        key = (rest, e)
        got = self._wcache.get(key)
        if got is None:
            ix = self.idx
            got = [ix[tuple(sorted(c + (e,)))]
                   for c in combinations(rest, self.t - 1)]
            if len(self._wcache) < 500000:
                self._wcache[key] = got
        return got


# ----------------------------- greedy core ---------------------------
def _grow_full(v, k, t, tix, uncov, rng):
    """Grow ONE block with exact max-gain evaluation at every step."""
    ix = tix.idx
    tsets = tix.tsets

    # seed: uncovered t-subset whose elements are globally hottest
    freq = [0] * v
    for i in uncov:
        for e in tsets[i]:
            freq[e] += 1
    best_i = -1
    best_s = -1
    for i in uncov:
        s = 0
        for e in tsets[i]:
            s += freq[e]
        if s > best_s:
            best_s = s
            best_i = i
    block = list(tsets[best_i])
    inb = set(block)

    t1 = t - 1
    while len(block) < k:
        gains = [0] * v
        if len(block) >= t1:
            for sub in combinations(sorted(block), t1):
                for x in range(v):
                    if x in inb:
                        continue
                    j = ix.get(tuple(sorted(sub + (x,))))
                    if j is not None and j in uncov:
                        gains[x] += 1
        best_x = -1
        best_g = -1
        ties = 0
        for x in range(v):
            if x in inb:
                continue
            g = gains[x]
            if g > best_g:
                best_g = g
                best_x = x
                ties = 1
            elif g == best_g:
                ties += 1
                if rng.randrange(ties) == 0:
                    best_x = x
        if best_x < 0:
            pool = [x for x in range(v) if x not in inb]
            best_x = rng.choice(pool)
        block.append(best_x)
        inb.add(best_x)
    return tuple(sorted(block))


def greedy_cover(v, k, t, tix, uncov, rng, deadline=None, on_partial=None):
    """Consume set-of-ids `uncov`; return list of blocks."""
    blocks = []
    cad = max(1, min(40, len(uncov) // 20 + 1))
    while uncov:
        if deadline is not None and time.perf_counter() > deadline:
            # emergency finish: cheap completion, but stay feasible
            while uncov:
                seed = next(iter(uncov))
                elems = list(tix.tsets[seed])
                pool = [x for x in range(v) if x not in set(elems)]
                rng.shuffle(pool)
                elems.extend(pool[:k - len(elems)])
                blk = tuple(sorted(elems))
                blocks.append(blk)
                for i in tix.block_ids(blk):
                    uncov.discard(i)
            break
        blk = _grow_full(v, k, t, tix, uncov, rng)
        blocks.append(blk)
        for i in tix.block_ids(blk):
            uncov.discard(i)
        if on_partial is not None and len(blocks) % cad == 0:
            on_partial(blocks)
    return blocks


# ------------------------- coverage bookkeeping ----------------------
def build_cov(blocks, tix):
    cov = [0] * tix.n
    for b in blocks:
        for i in tix.block_ids(b):
            cov[i] += 1
    return cov


def remove_redundant(blocks, tix, cov, rng, passes=5):
    out = list(blocks)
    for _ in range(passes):
        order = list(range(len(out)))
        rng.shuffle(order)
        keep = [True] * len(out)
        removed = False
        for i in order:
            ids = tix.block_ids(out[i])
            ok = True
            for j in ids:
                if cov[j] < 2:
                    ok = False
                    break
            if ok:
                for j in ids:
                    cov[j] -= 1
                keep[i] = False
                removed = True
        out = [b for i, b in enumerate(out) if keep[i]]
        if not removed:
            break
    return out


def dedupe(blocks, v, k, rng):
    """Guarantee no two identical blocks (evaluator violation)."""
    seen = set()
    out = []
    for b in blocks:
        if b in seen:
            for _ in range(100):
                lb = list(b)
                i = rng.randrange(k)
                pool = [x for x in range(v) if x not in set(lb)]
                if not pool:
                    break
                lb[i] = rng.choice(pool)
                nb = tuple(sorted(lb))
                if nb not in seen:
                    b = nb
                    break
        seen.add(b)
        out.append(b)
    return out


# ------------------- orbit-greedy cyclic skeleton --------------------
def orbit_of(v, base):
    """Orbit of `base` under x -> x + s (mod v)."""
    out = []
    seen = set()
    for s in range(v):
        nb = tuple(sorted((x + s) % v for x in base))
        if nb not in seen:
            seen.add(nb)
            out.append(nb)
    return out


def spread_base(v, k, rng):
    """Near-uniform spread base block (approximate difference set)."""
    step = max(1, v // k)
    base = []
    cur = rng.randrange(v)
    for _ in range(k):
        base.append(cur % v)
        cur += step + (1 if rng.random() < 0.35 else 0)
    base = list(dict.fromkeys(x % v for x in base))
    pool = [x for x in range(v) if x not in set(base)]
    rng.shuffle(pool)
    while len(base) < k and pool:
        base.append(pool.pop())
    return tuple(sorted(base[:k]))


def greedy_base(v, k, t, tix, cov, rng):
    """Greedy base block against the current coverage."""
    ix = tix.idx
    start = rng.randrange(v)
    block = [start]
    inb = {start}
    t1 = t - 1
    while len(block) < k:
        gains = [0] * v
        if len(block) >= t1:
            for sub in combinations(sorted(block), t1):
                for x in range(v):
                    if x in inb:
                        continue
                    j = ix.get(tuple(sorted(sub + (x,))))
                    if j is not None and cov[j] == 0:
                        gains[x] += 1
        best_x = -1
        best_g = -1
        ties = 0
        for x in range(v):
            if x in inb:
                continue
            g = gains[x]
            if g > best_g:
                best_g = g
                best_x = x
                ties = 1
            elif g == best_g:
                ties += 1
                if rng.randrange(ties) == 0:
                    best_x = x
        if best_x < 0:
            pool = [x for x in range(v) if x not in inb]
            best_x = rng.choice(pool)
        block.append(best_x)
        inb.add(best_x)
    return tuple(sorted(block))


def orbit_gain(orbit, tix, cov):
    touched = set()
    for b in orbit:
        for j in tix.block_ids(b):
            if cov[j] == 0:
                touched.add(j)
    return len(touched)


def orbit_skeleton(v, k, t, tix, rng, deadline, limit):
    """Greedily stack orbits (best new-coverage per block) until they stop
    paying; return (blocks, cov, remaining_uncovered)."""
    cov = [0] * tix.n
    remaining = tix.n
    blocks = []
    while remaining > 0 and len(blocks) < limit:
        if time.perf_counter() >= deadline:
            break
        best_orb = None
        best_gain = 0
        best_eff = 0.0
        for _ in range(ORBIT_CAND):
            if time.perf_counter() >= deadline:
                break
            r = rng.random()
            if r < 0.50:
                base = greedy_base(v, k, t, tix, cov, rng)
            elif r < 0.80:
                base = spread_base(v, k, rng)
            else:
                base = tuple(sorted(rng.sample(range(v), k)))
            orb = orbit_of(v, base)
            if not orb:
                continue
            g = orbit_gain(orb, tix, cov)
            if g == 0:
                continue
            eff = g / float(len(orb))
            if eff > best_eff:
                best_eff = eff
                best_gain = g
                best_orb = orb
        if best_orb is None:
            break
        # once an orbit covers less than ~1 new t-set per block, a targeted
        # greedy block is better: stop and patch instead.
        if best_gain < len(best_orb):
            break
        for b in best_orb:
            blocks.append(b)
            for j in tix.block_ids(b):
                if cov[j] == 0:
                    remaining -= 1
                cov[j] += 1
    return blocks, cov, remaining


# ---------------------- target-size local search ---------------------
class FixedSize:
    """Minimize #uncovered t-subsets using EXACTLY len(blocks) blocks."""

    def __init__(self, v, k, t, tix, blocks, rng):
        self.v, self.k, self.t = v, k, t
        self.tix = tix
        self.rng = rng
        self.blocks = [set(b) for b in blocks]
        self.cov = [0] * tix.n
        for b in self.blocks:
            for j in tix.block_ids(tuple(sorted(b))):
                self.cov[j] += 1
        self.uncov = {j for j, c in enumerate(self.cov) if c == 0}
        self.cost = len(self.uncov)
        self.where = [set() for _ in range(v)]
        for bi, b in enumerate(self.blocks):
            for e in b:
                self.where[e].add(bi)
        self.best_cost = self.cost
        self.best_snapshot = [tuple(sorted(b)) for b in self.blocks]

    def _swap_ids(self, bi, out_e, in_e):
        rest = tuple(sorted(self.blocks[bi] - {out_e}))
        return (self.tix.ids_with(rest, out_e),
                self.tix.ids_with(rest, in_e))

    def _delta(self, rem, add):
        cov = self.cov
        d = 0
        rset = set(rem)
        for j in rem:
            if cov[j] == 1:
                d += 1
        for j in set(add):
            c = cov[j]
            if j in rset:
                c -= 1
            if c == 0:
                d -= 1
        return d

    def _apply(self, bi, out_e, in_e, rem, add, d):
        cov = self.cov
        unc = self.uncov
        for j in rem:
            cov[j] -= 1
            if cov[j] == 0:
                unc.add(j)
        for j in add:
            if cov[j] == 0:
                unc.discard(j)
            cov[j] += 1
        self.blocks[bi].discard(out_e)
        self.blocks[bi].add(in_e)
        self.where[out_e].discard(bi)
        self.where[in_e].add(bi)
        self.cost += d

    def _random_kick(self):
        rng = self.rng
        bi = rng.randrange(len(self.blocks))
        blk = self.blocks[bi]
        out_e = rng.choice(sorted(blk))
        pool = [x for x in range(self.v) if x not in blk]
        if not pool:
            return
        in_e = rng.choice(pool)
        rem, add = self._swap_ids(bi, out_e, in_e)
        self._apply(bi, out_e, in_e, rem, add, self._delta(rem, add))

    def run(self, deadline):
        """Tabu search; returns True when a full covering is reached."""
        rng = self.rng
        nb = len(self.blocks)
        if nb == 0:
            return self.cost == 0
        tabu = {}
        tenure = max(4, int(TABU_FRAC * nb * self.k) + 3)
        it = 0
        stall = 0
        ref_cost = self.cost
        max_stall = max(50, 4 * nb)
        chk = 0
        tm1 = self.t - 1
        while self.cost > 0:
            chk += 1
            if (chk & 31) == 0 and time.perf_counter() > deadline:
                if self.cost < self.best_cost:
                    self.best_cost = self.cost
                    self.best_snapshot = [tuple(sorted(b))
                                          for b in self.blocks]
                return False
            it += 1
            if not self.uncov:
                break
            ul = list(self.uncov)
            tgt = self.tix.tsets[ul[rng.randrange(len(ul))]]
            tset = set(tgt)
            # blocks reachable by one swap contain exactly t-1 target elems
            cnt = {}
            for e in tgt:
                for bi in self.where[e]:
                    cnt[bi] = cnt.get(bi, 0) + 1
            cands = [bi for bi, c in cnt.items() if c == tm1]
            best = None
            best_d = None
            for bi in cands:
                blk = self.blocks[bi]
                miss = tset - blk
                if len(miss) != 1:
                    continue
                in_e = next(iter(miss))
                for out_e in [e for e in blk if e not in tset]:
                    rem, add = self._swap_ids(bi, out_e, in_e)
                    d = self._delta(rem, add)
                    if (tabu.get((bi, out_e, in_e), 0) > it
                            and self.cost + d >= self.best_cost):
                        continue
                    if best_d is None or d < best_d or (
                            d == best_d and rng.random() < 0.30):
                        best_d = d
                        best = (bi, out_e, in_e, rem, add)
            if best is None:
                self._random_kick()
                stall += 1
            else:
                bi, out_e, in_e, rem, add = best
                self._apply(bi, out_e, in_e, rem, add, best_d)
                tabu[(bi, in_e, out_e)] = it + tenure + rng.randrange(4)
                if self.cost < ref_cost:
                    ref_cost = self.cost
                    stall = 0
                else:
                    stall += 1
            if self.cost < self.best_cost:
                self.best_cost = self.cost
                self.best_snapshot = [tuple(sorted(b)) for b in self.blocks]
            if stall > max_stall:
                for _ in range(3):
                    self._random_kick()
                tabu.clear()
                stall = 0
                ref_cost = self.cost
        if self.cost < self.best_cost:
            self.best_cost = self.cost
            self.best_snapshot = [tuple(sorted(b)) for b in self.blocks]
        return self.cost == 0

    def tuples(self):
        return [tuple(sorted(b)) for b in self.blocks]


# -------------------------------- solve ------------------------------
def solve(v, k, t, budget, seed=0, on_improve=None):
    rng = random.Random(seed * 7919 + 17)
    t0 = time.perf_counter()
    deadline = t0 + budget
    tix = TIndex(v, t)

    def emit(bs):
        if on_improve is not None:
            on_improve([tuple(x + 1 for x in b) for b in bs], True)

    def emit_partial(bs):
        if on_improve is not None:
            on_improve([tuple(x + 1 for x in b) for b in bs], False)

    # -------- Phase A: greedy => immediate feasibility ---------------
    blocks = greedy_cover(v, k, t, tix, set(range(tix.n)), rng,
                          deadline=min(deadline - 0.3, t0 + budget * 0.5),
                          on_partial=emit_partial)
    cov = build_cov(blocks, tix)
    best = remove_redundant(blocks, tix, cov, rng)
    emit(best)

    # -------- Phase B: orbit-greedy cyclic skeleton -------------------
    orb_dl = min(deadline - 0.4, t0 + budget * (0.5 + ORBIT_FRAC))
    rounds = 0
    while time.perf_counter() < orb_dl and rounds < ORBIT_ROUNDS:
        rounds += 1
        sk, cov_s, rem = orbit_skeleton(v, k, t, tix, rng, orb_dl,
                                        limit=max(1, len(best) - 1))
        if not sk:
            break
        if rem > 0:
            holes = {j for j in range(tix.n) if cov_s[j] == 0}
            fill_dl = min(deadline - 0.2, orb_dl + budget * 0.12)
            extra = greedy_cover(v, k, t, tix, holes, rng, deadline=fill_dl)
            sk = sk + extra
        cand = dedupe(sk, v, k, rng)
        cc = build_cov(cand, tix)
        if any(c == 0 for c in cc):
            continue
        cand = remove_redundant(cand, tix, cc, rng)
        if len(cand) < len(best):
            best = list(cand)
            emit(best)

    # -------- Phase C: diversified greedy restarts --------------------
    r_dl = t0 + min(budget * (0.5 + ORBIT_FRAC + RESTART_FRAC),
                    max(0.0, budget - 1.0))
    while time.perf_counter() < r_dl:
        blocks = greedy_cover(v, k, t, tix, set(range(tix.n)), rng,
                              deadline=r_dl)
        cov = build_cov(blocks, tix)
        blocks = remove_redundant(blocks, tix, cov, rng)
        if len(blocks) < len(best):
            best = list(blocks)
            emit(best)

    # -------- Phase D: persistent fixed-size search --------------------
    fs = None
    fs_target = None
    while time.perf_counter() < deadline - 0.05 and len(best) > 1:
        target = len(best) - 1
        if fs is None or fs_target != target:
            cov = build_cov(best, tix)
            scores = []
            for i, b in enumerate(best):
                uniq = 0
                for j in tix.block_ids(b):
                    if cov[j] == 1:
                        uniq += 1
                scores.append((uniq, i))
            scores.sort()
            pool = [i for _, i in scores[:max(1, len(scores) // 3)]]
            drop = rng.choice(pool)
            seed_blocks = [b for i, b in enumerate(best) if i != drop]
            fs = FixedSize(v, k, t, tix, seed_blocks, rng)
            fs_target = target

        rem = deadline - time.perf_counter()
        if rem <= 0.05:
            break
        sub_dl = time.perf_counter() + max(0.25, min(rem, rem * SLICE_FRAC))

        if fs.run(sub_dl):
            cand = dedupe(fs.tuples(), v, k, rng)
            cc = build_cov(cand, tix)
            if all(c > 0 for c in cc) and len(cand) < len(best):
                cand = remove_redundant(cand, tix, cc, rng)
                best = list(cand)
                emit(best)
            fs = None
            fs_target = None
            continue

        if time.perf_counter() >= deadline - 0.05:
            break
        # stalled: diversify the incumbent, then rebuild the search state
        rr_dl = min(deadline,
                    time.perf_counter()
                    + max(0.2, (deadline - time.perf_counter()) * 0.25))
        nb = ruin_recreate(v, k, t, tix, best, rng, rr_dl, emit)
        if len(nb) < len(best):
            best = nb
            fs = None
            fs_target = None
        else:
            fs = FixedSize(v, k, t, tix, fs.best_snapshot, rng)
            for _ in range(max(2, k // 2)):
                fs._random_kick()

    return [tuple(x + 1 for x in b) for b in best]


def ruin_recreate(v, k, t, tix, best, rng, deadline, emit):
    cur = list(best)
    cov = build_cov(cur, tix)
    while time.perf_counter() < deadline and len(cur) > 1:
        r = rng.randint(1, min(RUIN_MAX, len(cur) - 1))
        vic = set(rng.sample(range(len(cur)), r))
        victims = [cur[i] for i in vic]
        for b in victims:
            for j in tix.block_ids(b):
                cov[j] -= 1
        holes = set()
        for b in victims:
            for j in tix.block_ids(b):
                if cov[j] == 0:
                    holes.add(j)
        kept = [b for i, b in enumerate(cur) if i not in vic]
        added = greedy_cover(v, k, t, tix, set(holes), rng, deadline=deadline)
        if len(kept) + len(added) > len(cur):
            for b in victims:
                for j in tix.block_ids(b):
                    cov[j] += 1
            continue
        nb = dedupe(kept + added, v, k, rng)
        cov = build_cov(nb, tix)
        if any(c == 0 for c in cov):
            cur = list(cur)
            cov = build_cov(cur, tix)
            continue
        nb = remove_redundant(nb, tix, cov, rng)
        cov = build_cov(nb, tix)
        if len(nb) <= len(cur):
            cur = nb
            if len(cur) < len(best):
                best = list(cur)
                emit(best)
    return best


# --------------------------------- main -------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="covering design solver")
    ap.add_argument("instance")
    ap.add_argument("output")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    v, k, t = parse_instance_file(args.instance)
    budget = float(os.environ.get("COVERING_SEED_TIME_S", "10"))
    budget = max(1.0, min(budget, 50.0))

    state = {"n": None}

    def write(blocks, feasible):
        if state["n"] is not None and feasible and len(blocks) >= state["n"]:
            return
        _atomic_write(args.output, format_solution(blocks))
        if feasible:
            state["n"] = len(blocks)

    try:
        blocks = solve(v, k, t, budget, seed=args.seed, on_improve=write)
        if blocks:
            write(blocks, True)
    except Exception:
        if state["n"] is None:
            tix = TIndex(v, t)
            rng = random.Random(args.seed)
            bs = greedy_cover(v, k, t, tix, set(range(tix.n)), rng)
            _atomic_write(args.output,
                          format_solution([tuple(x + 1 for x in b)
                                           for b in bs]))
        raise SystemExit(0)


if __name__ == "__main__":
    main()