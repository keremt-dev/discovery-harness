"""Covering design solver C(v,k,t): minimize blocks covering all t-subsets.

MAIN LEVER -- affine geometry under the translation group.  If v = p^m
(p prime) and p^d <= k with d >= t-1, then any t points of AG(m,p) span an
affine subspace of dimension <= t-1 <= d, so the set of ALL d-flats (each
padded to k points when p^d < k) is a covering.  At v=32,k=8,t=4 that is
the 620 3-flats of AG(5,2) -- versus ~980 blocks for a max-gain greedy.
The flats are ENUMERATED from the group action (subspace closure + cosets),
never tabled, and the construction is only adopted when its size beats a
multiple of the LP bound C(v,t)/C(k,t).

A. Affine flats (or exact max-gain greedy when the geometry does not
   apply / is uncompetitive) => complete covering on disk within seconds.
B. Redundancy removal to a fixed point.
C. Fixed-size tabu search at b = |best|-1: single-element swaps guided by
   a random uncovered t-subset, directed forced-insert when no single swap
   reaches it, persistent tabu state, basin restarts (drop a different
   low-uniqueness block).
D. Ruin-and-recreate once the basin ladder is exhausted.

Every improvement is written atomically (os.replace).  Phase lengths are
work counters; wall clock is only the hard stop.  Deterministic per seed.

CLI: python solver.py <instance.cover> <output.txt> [--seed N]
Env: COVERING_SEED_TIME_S (default 10).
"""

import argparse
import os
import random
import time
from itertools import combinations

TABU_FRAC = 0.11
RUIN_MAX = 4
SLICE_FRAC = 0.80
CLOSE_FRAC = 3.0
TARGET_TRIES = 6
RESTART_N = 3
AG_SLACK = 2.5            # adopt flats only if count <= AG_SLACK * LP bound


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


def _binom(n, r):
    if r < 0 or r > n:
        return 0
    num = 1
    for i in range(r):
        num = num * (n - i) // (i + 1)
    return num


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
        self._scache = {}
        # Pair table rows[e][S] = id(S + {e}) for every sorted (t-1)-tuple S.
        # v*C(v,t-1) ints (159k at v=32,t=4): every swap evaluation is two
        # plain dict gets with no tuple sorting anywhere on the hot path.
        rows = self._ptab = [dict() for _ in range(v)]
        for i, ts in enumerate(self.tsets):
            for pos in range(t):
                rows[ts[pos]][ts[:pos] + ts[pos + 1:]] = i

    def block_ids(self, block):
        got = self._bcache.get(block)
        if got is None:
            ix = self.idx
            got = [ix[c] for c in combinations(block, self.t)]
            if len(self._bcache) < 300000:
                self._bcache[block] = got
        return got

    def sub_ids(self, sub):
        """(x, id) for every x outside the sorted (t-1)-tuple `sub`, read
        straight off the pair table (no tuple(sorted()) allocations)."""
        got = self._scache.get(sub)
        if got is None:
            ss = set(sub)
            rows = self._ptab
            got = [(x, rows[x][sub]) for x in range(self.v) if x not in ss]
            if len(self._scache) < 400000:
                self._scache[sub] = got
        return got


# ------------------- affine-geometry construction --------------------
def affine_blocks(v, k, t, rng):
    """All d-flats of AG(m,p) as k-blocks, or None if not applicable."""
    if v > 512:
        return None
    p = None
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if v % q == 0:
            p = q
            break
    if p is None:
        return None
    m, x = 0, 1
    while x < v:
        x *= p
        m += 1
    if x != v:
        return None
    d, y = 0, 1
    while y * p <= k:
        y *= p
        d += 1
    if d < t - 1:
        return None

    # digit-wise addition mod p == the translation group of AG(m,p)
    add = []
    for a in range(v):
        row = [0] * v
        for b in range(v):
            s, mul, aa, bb = 0, 1, a, b
            for _ in range(m):
                s += (((aa % p) + (bb % p)) % p) * mul
                aa //= p
                bb //= p
                mul *= p
            row[b] = s
        add.append(row)

    # all d-dimensional linear subspaces, by repeated closure
    spans = [frozenset((0,))]
    for _ in range(d):
        seen = set()
        nxt = []
        for sp in spans:
            for g in range(1, v):
                if g in sp:
                    continue
                ns = set(sp)
                cur = 0
                for _ in range(p - 1):
                    cur = add[cur][g]
                    arow = add[cur]
                    for s in sp:
                        ns.add(arow[s])
                fs = frozenset(ns)
                if fs not in seen:
                    seen.add(fs)
                    nxt.append(fs)
        spans = nxt
        if not spans:
            return None

    # cosets => the d-flats
    seenb = set()
    out = []
    for sp in spans:
        for a in range(v):
            arow = add[a]
            blk = tuple(sorted(arow[s] for s in sp))
            if blk not in seenb:
                seenb.add(blk)
                out.append(blk)
    if not out:
        return None

    pad = k - len(out[0])
    if pad > 0:
        res = []
        for blk in out:
            inb = set(blk)
            pool = [z for z in range(v) if z not in inb]
            rng.shuffle(pool)
            res.append(tuple(sorted(blk + tuple(pool[:pad]))))
        out = res
    return out


# ----------------------------- greedy core ---------------------------
def _pick_best(v, inb, gains, rng):
    best_x, best_g, ties = -1, -1, 0
    for x in range(v):
        if x in inb:
            continue
        g = gains[x]
        if g > best_g:
            best_g, best_x, ties = g, x, 1
        elif g == best_g:
            ties += 1
            if rng.randrange(ties) == 0:
                best_x = x
    if best_x < 0:
        best_x = rng.choice([x for x in range(v) if x not in inb])
    return best_x


def _grow_full(v, k, t, tix, uncov, rng):
    """Grow ONE block with exact max-gain evaluation at every step."""
    tsets = tix.tsets
    freq = [0] * v
    for i in uncov:
        for e in tsets[i]:
            freq[e] += 1
    best_i, best_s = -1, -1
    for i in uncov:
        s = 0
        for e in tsets[i]:
            s += freq[e]
        if s > best_s:
            best_s, best_i = s, i
    block = list(tsets[best_i])
    inb = set(block)
    t1 = t - 1
    sub_ids = tix.sub_ids
    while len(block) < k:
        gains = [0] * v
        if len(block) >= t1:
            for sub in combinations(sorted(block), t1):
                for x, j in sub_ids(sub):
                    if j in uncov:
                        gains[x] += 1
        x = _pick_best(v, inb, gains, rng)
        block.append(x)
        inb.add(x)
    return tuple(sorted(block))


def greedy_cover(v, k, t, tix, uncov, rng, deadline=None, on_partial=None):
    blocks = []
    cad = max(1, min(40, len(uncov) // 20 + 1))
    while uncov:
        if deadline is not None and time.perf_counter() > deadline:
            while uncov:  # emergency finish: cheap, but stay feasible
                elems = list(tix.tsets[next(iter(uncov))])
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


def uniq_scores(blocks, tix, cov):
    scores = []
    for i, b in enumerate(blocks):
        u = 0
        for j in tix.block_ids(b):
            if cov[j] == 1:
                u += 1
        scores.append((u, i))
    scores.sort()
    return scores


# ---------------------- target-size local search ---------------------
class FixedSize:
    """Minimize #uncovered t-subsets using EXACTLY len(blocks) blocks."""

    def __init__(self, v, k, t, tix, blocks, rng):
        self.v, self.k, self.t = v, k, t
        self.tix = tix
        self.rng = rng
        self.prow = tix._ptab
        self._sc = {}
        self._tabu = {}
        self._it = 0
        self.best_snapshot = [tuple(sorted(b)) for b in blocks]
        self.best_cost = 1 << 30
        self.restore_best()
        self.best_cost = self.cost

    def restore_best(self):
        """Reset to the best snapshot and drop the tabu memory (the memory is
        what is stuck, not the assignment)."""
        tix = self.tix
        self.btup = list(self.best_snapshot)
        self.blocks = [set(b) for b in self.btup]
        cov = self.cov = [0] * tix.n
        for bt in self.btup:
            for j in tix.block_ids(bt):
                cov[j] += 1
        self.uncov = {j for j, c in enumerate(cov) if c == 0}
        self.cost = len(self.uncov)
        self.where = [set() for _ in range(self.v)]
        for bi, b in enumerate(self.blocks):
            for e in b:
                self.where[e].add(bi)
        self._tabu = {}

    def _subs(self, rest):
        got = self._sc.get(rest)
        if got is None:
            got = list(combinations(rest, self.t - 1))
            if len(self._sc) < 400000:
                self._sc[rest] = got
        return got

    def _swap_ids(self, bi, out_e, in_e):
        """Ids broken / created by replacing out_e with in_e in block bi: one
        linear scan of the sorted mirror plus two dict gets per (t-1)-set."""
        sub = self._subs(tuple(e for e in self.btup[bi] if e != out_e))
        ro = self.prow[out_e]
        ri = self.prow[in_e]
        return ([ro[c] for c in sub], [ri[c] for c in sub])

    def _delta(self, rem, add):
        """rem and add are DISJOINT, so no overlap bookkeeping is needed."""
        cov = self.cov
        d = 0
        for j in rem:
            if cov[j] == 1:
                d += 1
        for j in add:
            if cov[j] == 0:
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
        blk = self.blocks[bi]
        blk.discard(out_e)
        blk.add(in_e)
        lst = [e for e in self.btup[bi] if e != out_e]
        lo, hi = 0, len(lst)
        while lo < hi:
            mid = (lo + hi) >> 1
            if lst[mid] < in_e:
                lo = mid + 1
            else:
                hi = mid
        lst.insert(lo, in_e)
        self.btup[bi] = tuple(lst)
        self.where[out_e].discard(bi)
        self.where[in_e].add(bi)
        self.cost += d

    def _forced_insert(self, tgt, tset, cnt):
        """Force the whole target t-set into ONE block via a chain of single
        swaps, each eviction chosen by real delta -- directed replacement for
        the blind kick (a block sharing t-1 target elements is often rare)."""
        rng = self.rng
        if cnt:
            top = max(cnt.values())
            pool = [bi for bi, c in cnt.items() if c == top]
        else:
            pool = [rng.randrange(len(self.blocks))]
        bi = pool[rng.randrange(len(pool))]
        for _ in range(self.t):
            blk = self.blocks[bi]
            miss = [e for e in tgt if e not in blk]
            if not miss:
                break
            in_e = miss[rng.randrange(len(miss))]
            best = None
            best_d = None
            for out_e in self.btup[bi]:
                if out_e in tset:
                    continue
                rem, add = self._swap_ids(bi, out_e, in_e)
                d = self._delta(rem, add)
                if best_d is None or d < best_d or (
                        d == best_d and rng.random() < 0.35):
                    best_d = d
                    best = (out_e, rem, add)
            if best is None:
                break
            out_e, rem, add = best
            self._apply(bi, out_e, in_e, rem, add, best_d)

    def _random_kick(self):
        rng = self.rng
        bi = rng.randrange(len(self.blocks))
        blk = self.blocks[bi]
        bt = self.btup[bi]
        out_e = bt[rng.randrange(len(bt))]
        pool = [x for x in range(self.v) if x not in blk]
        if not pool:
            return
        in_e = rng.choice(pool)
        rem, add = self._swap_ids(bi, out_e, in_e)
        self._apply(bi, out_e, in_e, rem, add, self._delta(rem, add))

    def _track(self):
        if self.cost < self.best_cost:
            self.best_cost = self.cost
            self.best_snapshot = list(self.btup)

    def run(self, deadline):
        """Tabu search; True when a full covering is reached.  Tabu memory and
        the iteration clock persist across slices at this target size."""
        rng = self.rng
        nb = len(self.blocks)
        if nb == 0:
            return self.cost == 0
        tabu = self._tabu
        tenure = max(4, int(TABU_FRAC * nb * self.k) + 3)
        it = self._it
        stall = 0
        ref_cost = self.cost
        max_stall = max(50, 4 * nb)
        chk = 0
        tm1 = self.t - 1
        tsets = self.tix.tsets
        while self.cost > 0:
            chk += 1
            if (chk & 31) == 0 and time.perf_counter() > deadline:
                self._it = it
                self._track()
                return False
            it += 1
            if not self.uncov:
                break
            ul = list(self.uncov)
            tgt = tsets[ul[rng.randrange(len(ul))]]
            tset = set(tgt)
            cnt = {}
            for e in tgt:
                for bi in self.where[e]:
                    cnt[bi] = cnt.get(bi, 0) + 1
            cands = [bi for bi, c in cnt.items() if c == tm1]
            if not cands:
                self._forced_insert(tgt, tset, cnt)
                stall += 1
                self._track()
                continue
            best = None
            best_d = None
            for bi in cands:
                miss = tset - self.blocks[bi]
                if len(miss) != 1:
                    continue
                in_e = next(iter(miss))
                for out_e in self.btup[bi]:
                    if out_e in tset:
                        continue
                    rem, add = self._swap_ids(bi, out_e, in_e)
                    d = self._delta(rem, add)
                    if (tabu.get((bi, out_e, in_e), 0) > it
                            and self.cost + d >= self.best_cost):
                        continue
                    if best_d is None or d < best_d or (
                            d == best_d and rng.random() < 0.30):
                        best_d = d
                        best = (bi, out_e, in_e, rem, add)
                        if d < -1:
                            break
                if best_d is not None and best_d < -1:
                    break
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
            self._track()
            if stall > max_stall:
                for _ in range(3):
                    self._random_kick()
                tabu.clear()
                stall = 0
                ref_cost = self.cost
        self._it = it
        self._track()
        return self.cost == 0

    def tuples(self):
        return list(self.btup)


# -------------------------------- solve ------------------------------
def solve(v, k, t, budget, seed=0, on_improve=None):
    rng = random.Random(seed * 7919 + 17)
    deadline = time.perf_counter() + budget
    tix = TIndex(v, t)

    def emit(bs):
        if on_improve is not None:
            on_improve([tuple(x + 1 for x in b) for b in bs], True)

    def emit_partial(bs):
        if on_improve is not None:
            on_improve([tuple(x + 1 for x in b) for b in bs], False)

    lp = tix.n / float(max(1, _binom(k, t)))
    best = None

    # -------- Phase A1: affine-geometry flats -------------------------
    fl = affine_blocks(v, k, t, rng)
    if fl and len(fl) <= AG_SLACK * lp:
        fl = dedupe(fl, v, k, rng)
        cov = build_cov(fl, tix)
        if all(c > 0 for c in cov):
            best = remove_redundant(fl, tix, cov, rng)
            emit(best)

    # -------- Phase A2: exact max-gain greedy (+ restarts) ------------
    if best is None or len(best) > 2.0 * lp:
        blocks = greedy_cover(v, k, t, tix, set(range(tix.n)), rng,
                              deadline=deadline - 0.3,
                              on_partial=emit_partial if best is None else None)
        cand = remove_redundant(blocks, tix, build_cov(blocks, tix), rng)
        if best is None or len(cand) < len(best):
            best = cand
            emit(best)
        restarts = 0
        while restarts < RESTART_N and time.perf_counter() < deadline - 1.0:
            restarts += 1
            bl = greedy_cover(v, k, t, tix, set(range(tix.n)), rng,
                              deadline=deadline - 0.5)
            bl = remove_redundant(bl, tix, build_cov(bl, tix), rng)
            if len(bl) < len(best):
                best = list(bl)
                emit(best)

    # -------- Phase C: fixed-size search over basins ------------------
    def make_fs(bs, rank):
        """Drop one block among the least-unique third (`rank` picks which,
        i.e. which basin) and search the remainder at size |bs|-1."""
        scores = uniq_scores(bs, tix, build_cov(bs, tix))
        pool = [i for _, i in scores[:max(1, len(scores) // 3)]]
        drop = pool[rank % len(pool)]
        return FixedSize(v, k, t, tix,
                         [b for i, b in enumerate(bs) if i != drop], rng)

    fs = None
    fs_target = None
    tries = 0
    drop_rank = 0
    while time.perf_counter() < deadline - 0.05 and len(best) > 1:
        target = len(best) - 1
        if fs is None or fs_target != target:
            drop_rank = rng.randrange(1 << 20)
            fs = make_fs(best, drop_rank)
            fs_target = target
            tries = 0

        rem = deadline - time.perf_counter()
        if rem <= 0.05:
            break
        sub_dl = time.perf_counter() + max(0.25, min(rem, rem * SLICE_FRAC))

        if fs.run(sub_dl):
            cand = dedupe(fs.tuples(), v, k, rng)
            cc = build_cov(cand, tix)
            if all(c > 0 for c in cc) and len(cand) < len(best):
                best = remove_redundant(cand, tix, cc, rng)
                emit(best)
            fs = None
            fs_target = None
            continue

        tries += 1
        # Close to solved: keep hammering the SAME basin.
        if fs.best_cost <= max(2, int(CLOSE_FRAC * k)):
            fs.restore_best()
            for _ in range(2):
                fs._random_kick()
            continue
        # Far off: same size, different basin.
        if tries < TARGET_TRIES:
            drop_rank += 1
            fs = make_fs(best, drop_rank)
            continue

        if time.perf_counter() >= deadline - 0.05:
            break
        rr_dl = min(deadline, time.perf_counter()
                    + max(0.2, (deadline - time.perf_counter()) * 0.20))
        nb = ruin_recreate(v, k, t, tix, best, rng, rr_dl, emit)
        if len(nb) < len(best):
            best = nb
        fs = None
        fs_target = None

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
    budget = max(1.0, min(budget, 305.0))

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