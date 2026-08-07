# EVRILEN COZUCU v2 — dondurulmus artefakt (2026-08-05)
# Kaynak kosu: runs/evolve/bench-v2-dilim1 (Opus, 50 iter; baslangic genomu
# best_20260805.py, buyuk-n fitness seti: train-router-n500-m12-s7 +
# train-enerji-n300-m10-s14 + train-router-n20-m4-s10, set skoru 0.6900).
# Yapisal fark: K-kesimli absorbing konvolusyon DP (O(K), n-bagimsiz) +
# butceye dayanikli kurulum + olcek-farkindali coklu-birim takas.
# DEGISTIRILMEZ; benchmark degerlendirmelerinde "evrilen-v2" kolonu budur.
# Multi-type weighted k-out-of-n:G reliability maximization under budget.
# Strategy: K-truncated convolution DP (absorbing bucket at >= K) for O(K)
# reliability evaluation independent of total weight; cheapest-feasible
# construction + marginal-gain upgrades; scale-aware multi-unit exchange
# local search with prefix caching; deterministic ILS with time budget.
import os, sys, time, random
import numpy as np


def parse(path):
    H, T = {}, {}
    with open(path) as fh:
        for raw in fh:
            L = raw.split('#', 1)[0].strip()
            if not L:
                continue
            p = L.split()
            if p[0] == 'TYPE':
                T[int(p[1])] = (float(p[2]), float(p[3]), float(p[4]))
            else:
                H[p[0]] = p[1]
    m = int(H['M'])
    ts = [T[j] for j in range(1, m + 1)]
    return (int(H['N']), float(H['K']), float(H['BUDGET']),
            [t[0] for t in ts], [t[1] for t in ts], [t[2] for t in ts])


def find_scale(vals):
    for s in (1, 2, 4, 5, 8, 10, 16, 20, 25, 32, 40, 50, 64, 100,
              125, 200, 250, 500, 1000):
        ok = True
        for v in vals:
            if abs(v * s - round(v * s)) > 1e-9:
                ok = False
                break
        if ok:
            return s
    return None


class Rel:
    """Reliability oracle: P(sum of working weights >= K).

    Integer-weight path uses a DP truncated at K: index i < K means
    'accumulated weight exactly i', index K means 'reached K or more'
    (absorbing).  Cost per type-block is O(K * n_j) worst case but the
    block PMF itself is built once per (type, count) and cached, so the
    dominant cost is a single length-(K+1) convolution per type.
    """

    def __init__(self, W, R, K):
        self.W, self.R, self.K = W, R, K
        self.m = len(W)
        sc = find_scale(list(W) + [K])
        self.exact = sc is not None
        if self.exact:
            self.iw = [int(round(w * sc)) for w in W]
            self.ik = int(round(K * sc))
            if self.ik <= 0:
                self.ik = 0
        self._blk = {}
        self._calls = 0

    # ---- per-type block pmf over weight, truncated at ik ------------
    def block(self, j, n):
        key = (j, n)
        b = self._blk.get(key)
        if b is not None:
            return b
        ik = self.ik
        w = self.iw[j]
        p = self.R[j]
        q = 1.0 - p
        span = min(n * w, ik)
        u = np.zeros(span + 1)
        if n == 0:
            u[0] = 1.0
        elif q < 1e-15:
            u[span] = 1.0
        elif p < 1e-15:
            u[0] = 1.0
        elif w == 0:
            u[0] = 1.0
        else:
            # binomial pmf over count of working units
            pb = q ** n
            if pb == 0.0:
                # underflow: work in logs
                from math import lgamma, log, exp
                lp, lq = log(p), log(q)
                for i in range(n + 1):
                    lv = (lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1)
                          + i * lp + (n - i) * lq)
                    v = exp(lv)
                    idx = i * w
                    if idx >= span:
                        u[span] += v
                    else:
                        u[idx] += v
            else:
                for i in range(n + 1):
                    idx = i * w
                    if idx >= span:
                        u[span] += pb
                    else:
                        u[idx] += pb
                    if i < n:
                        pb *= p * (n - i) / (q * (i + 1))
        self._blk[key] = u
        return u

    @staticmethod
    def _conv(pr, u, ik):
        """Convolve state vector pr (len ik+1, last=absorbing) with block u."""
        if len(u) == 1:
            return pr
        tail = pr[ik]                      # already absorbed mass
        c = np.convolve(pr[:ik], u)
        if len(c) > ik:
            head = c[:ik]
            tail = tail + c[ik:].sum()
        else:
            head = np.zeros(ik)
            head[:len(c)] = c
        out = np.empty(ik + 1)
        out[:ik] = head
        out[ik] = tail
        return out

    def __call__(self, A):
        self._calls += 1
        if self.exact:
            ik = self.ik
            if ik <= 0:
                return 1.0
            # quick bound: max attainable weight
            mx = 0
            for j, n in enumerate(A):
                if n:
                    mx += n * self.iw[j]
                    if mx >= ik:
                        break
            if mx < ik:
                return 0.0
            pr = np.zeros(ik + 1)
            pr[0] = 1.0
            for j, n in enumerate(A):
                if n:
                    pr = self._conv(pr, self.block(j, n), ik)
            return float(pr[ik])
        return self._float_rel(A)

    # ---- prefix machinery for cheap two-type re-evaluation ----------
    def prefix(self, A):
        """Return list P where P[t] = state after folding types 0..t-1."""
        ik = self.ik
        pr = np.zeros(ik + 1)
        pr[0] = 1.0
        out = [pr]
        for j in range(self.m):
            n = A[j]
            if n:
                pr = self._conv(pr, self.block(j, n), ik)
            out.append(pr)
        return out

    def from_prefix(self, P, A, start):
        """Reliability of A given prefix states P valid up to index start."""
        ik = self.ik
        pr = P[start]
        for j in range(start, self.m):
            n = A[j]
            if n:
                pr = self._conv(pr, self.block(j, n), ik)
        return float(pr[ik])

    # ---- fallback: irrational weights, dict DP ----------------------
    def _float_rel(self, A):
        K = self.K
        d = {0.0: 1.0}
        acc = 0.0
        for j, n in enumerate(A):
            if n == 0:
                continue
            w, p = self.W[j], self.R[j]
            q = 1.0 - p
            td = {}
            if q < 1e-15:
                td[n * w] = 1.0
            elif p < 1e-15:
                td[0.0] = 1.0
            else:
                pb = q ** n
                for i in range(n + 1):
                    wt = i * w
                    td[wt] = td.get(wt, 0.0) + pb
                    if i < n:
                        pb *= p * (n - i) / (q * (i + 1))
            nd = {}
            for aw, ap in d.items():
                for tw, tp in td.items():
                    s = aw + tw
                    v = ap * tp
                    if s >= K - 1e-9:
                        acc += v
                    else:
                        nd[s] = nd.get(s, 0.0) + v
            d = nd
            if not d:
                break
        return acc


def dominance(W, C, R):
    """Types j dominated by i (>=w, <=c, >=p, strict somewhere) are flagged."""
    m = len(W)
    alive = [True] * m
    for j in range(m):
        for i in range(m):
            if i == j or not alive[i]:
                continue
            if (W[i] >= W[j] - 1e-12 and C[i] <= C[j] + 1e-12
                    and R[i] >= R[j] - 1e-12):
                if (W[i] > W[j] + 1e-12 or C[i] < C[j] - 1e-12
                        or R[i] > R[j] + 1e-12):
                    alive[j] = False
                    break
    return alive


def base_alloc(n, budget, C):
    """All-cheapest allocation: the feasibility anchor."""
    m = len(C)
    cj = min(range(m), key=lambda x: C[x])
    A = [0] * m
    A[cj] = n
    return A, n * C[cj], cj


def upgrade_greedy(n, budget, C, rel, A0, cost0, deadline, alive):
    """Repeatedly move one unit from some type to another if it helps."""
    m = len(C)
    A = list(A0)
    cost = cost0
    cur = rel(A)
    while time.perf_counter() < deadline:
        best = None
        for a in range(m):
            if A[a] == 0:
                continue
            for b in range(m):
                if b == a or not alive[b]:
                    continue
                d = C[b] - C[a]
                if cost + d > budget + 1e-9:
                    continue
                A[a] -= 1
                A[b] += 1
                r = rel(A)
                A[a] += 1
                A[b] -= 1
                if r > cur + 1e-13:
                    g = r - cur
                    # prefer cheap gains as tie-break
                    if best is None or g > best[0] + 1e-15:
                        best = (g, a, b, r, d)
        if best is None:
            break
        _, a, b, r, d = best
        A[a] -= 1
        A[b] += 1
        cost += d
        cur = r
    return A, cost, cur


def solve(n, k, budget, W, C, R, tbs):
    m = len(C)
    t0 = time.perf_counter()
    deadline = t0 + tbs
    rel = Rel(W, R, k)
    alive = dominance(W, C, R)
    cheap = min(range(m), key=lambda x: C[x])
    alive[cheap] = True  # always keep the feasibility anchor

    if n * min(C) > budget + 1e-9:
        # infeasible by construction; emit cheapest anyway
        A = [0] * m
        A[cheap] = n
        return A

    # ---------- candidate pool ----------
    cands = []

    def gfill(order):
        """Greedy fill respecting the 'must place all n' constraint."""
        mc = min(C)
        A = [0] * m
        money = 0.0
        for s in range(n):
            rem = n - s - 1
            placed = False
            for j in order:
                if money + C[j] + rem * mc <= budget + 1e-9:
                    A[j] += 1
                    money += C[j]
                    placed = True
                    break
            if not placed:
                A[cheap] += 1
                money += C[cheap]
        return A, money

    idxs = [j for j in range(m) if alive[j]]
    keys = [
        lambda j: -(W[j] * R[j] / C[j]),
        lambda j: -(W[j] / C[j]),
        lambda j: -(W[j] * R[j]),
        lambda j: -R[j],
        lambda j: -(W[j] * R[j] ** 2 / C[j]),
        lambda j: -(W[j] * R[j] - k / max(n, 1)) / C[j],
        lambda j: C[j],
    ]
    for key in keys:
        o = sorted(idxs, key=key) + [j for j in range(m) if not alive[j]]
        cands.append(gfill(o)[0])
    for f in idxs:
        o = [f] + [j for j in range(m) if j != f]
        cands.append(gfill(o)[0])
    if len(idxs) <= 8:
        for ii in range(len(idxs)):
            for jj in range(ii + 1, len(idxs)):
                i, j = idxs[ii], idxs[jj]
                o = [i, j] + [x for x in range(m) if x != i and x != j]
                cands.append(gfill(o)[0])

    # anchor + budget-driven marginal upgrade (robust at large N)
    A0, c0, _ = base_alloc(n, budget, C)
    cands.append(A0)

    best = None
    br = -1.0
    for a in cands:
        if sum(a) != n:
            continue
        if sum(c * x for c, x in zip(C, a)) > budget + 1e-9:
            continue
        r = rel(a)
        if r > br:
            br, best = r, list(a)
    if best is None:
        best, br = A0, rel(A0)

    # marginal-gain upgrade from the anchor, time permitting
    if time.perf_counter() < t0 + 0.35 * tbs:
        ua, uc, ur = upgrade_greedy(n, budget, C, rel, A0, c0,
                                    t0 + 0.35 * tbs, alive)
        if ur > br:
            br, best = ur, list(ua)

    # ---------- iterated local search ----------
    cur = list(best)
    cr = br
    cm = sum(c * x for c, x in zip(C, cur))
    rng = random.Random(987654321)

    # scale-aware step sizes: single-unit moves are useless at N=500
    steps = []
    s = 1
    while s <= max(1, n // 2):
        steps.append(s)
        s = s * 2 if s < 8 else int(s * 1.7) + 1
    if n >= 4 and n // 4 not in steps:
        steps.append(n // 4)
    steps = sorted(set(x for x in steps if 1 <= x <= n))

    use_prefix = rel.exact and rel.ik > 0

    while time.perf_counter() < deadline:
        improved = True
        while improved and time.perf_counter() < deadline:
            improved = False
            P = rel.prefix(cur) if use_prefix else None
            for t in steps:
                if improved:
                    break
                for a in range(m):
                    if cur[a] < t:
                        continue
                    for b in range(m):
                        if b == a or not alive[b]:
                            continue
                        cd = (C[b] - C[a]) * t
                        if cm + cd > budget + 1e-9:
                            continue
                        cur[a] -= t
                        cur[b] += t
                        if use_prefix:
                            r = rel.from_prefix(P, cur, min(a, b))
                        else:
                            r = rel(cur)
                        if r > cr + 1e-13:
                            cr = r
                            cm += cd
                            improved = True
                            break
                        cur[a] += t
                        cur[b] -= t
                    if improved:
                        break
            if time.perf_counter() >= deadline:
                break

        if cr > br + 1e-13:
            br = cr
            best = list(cur)
        else:
            cur = list(best)
            cr = br
            cm = sum(c * x for c, x in zip(C, cur))

        if time.perf_counter() >= deadline:
            break

        # perturbation sized relative to N
        kick = max(1, n // 20)
        for _ in range(rng.randint(1, 3)):
            a = rng.randrange(m)
            b = rng.randrange(m)
            if a == b or cur[a] == 0 or not alive[b]:
                continue
            t = rng.randint(1, min(kick, cur[a]))
            cd = (C[b] - C[a]) * t
            while t > 0 and cm + cd > budget + 1e-9:
                t -= 1
                cd = (C[b] - C[a]) * t
            if t <= 0:
                continue
            cur[a] -= t
            cur[b] += t
            cm += cd
        cr = rel(cur)

    # final safety: enforce feasibility
    if sum(best) != n or sum(c * x for c, x in zip(C, best)) > budget + 1e-9:
        best = A0
    return best


def main():
    path, out = sys.argv[1], sys.argv[2]
    tbs = float(os.environ.get("KOFN_TIME", "40"))
    tbs = max(1.0, min(tbs, 50.0))
    n, k, budget, W, C, R = parse(path)
    alloc = solve(n, k, budget, W, C, R, tbs * 0.92)
    rel = Rel(W, R, k)
    rv = rel(alloc)
    with open(out, "w") as f:
        f.write("R %.9f\n" % rv)
        f.write(" ".join(map(str, alloc)) + "\n")


if __name__ == "__main__":
    main()