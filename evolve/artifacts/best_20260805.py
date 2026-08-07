# EVRILEN COZUCU — dondurulmus artefakt (2026-08-05)
# Kaynak kosu: runs/evolve/gen-sert-n25-m5-s3-mix3 (GLM Dilim-1 + Opus dogrulama)
# Set skoru 0.7228: n25-m5-s3 kanitli optimum / n60-m10-s4 refsearch esiti /
# n100-m6-s4 refsearch+0.032. Tavan kaniti: docs/faz-e-gradyan.md.
# Benchmark v1 degerlendirmesinde "evrilen" kolonu bu dosyadir; DEGISTIRILMEZ.
import os, sys, time, random
import numpy as np

def parse(path):
    H, T = {}, {}
    for raw in open(path):
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
    for s in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]:
        if all(abs(v * s - round(v * s)) < 1e-9 for v in vals):
            return s
    return None


def make_rel(W, R, K):
    sc = find_scale(W + [K])
    if sc:
        iw = [int(round(w * sc)) for w in W]
        ik = int(round(K * sc))

        def rel(A):
            mx = sum(n * iw[j] for j, n in enumerate(A) if n > 0)
            if mx < ik:
                return 0.0
            pr = np.zeros(mx + 1)
            pr[0] = 1.0
            for j, n in enumerate(A):
                if n == 0:
                    continue
                w, p = iw[j], R[j]
                q = 1.0 - p
                u = np.zeros(n * w + 1)
                if q < 1e-15:
                    u[n * w] = 1.0
                elif p < 1e-15:
                    u[0] = 1.0
                else:
                    pb = q ** n
                    for i in range(n + 1):
                        u[i * w] = pb
                        if i < n:
                            pb *= p * (n - i) / (q * (i + 1))
                pr = np.convolve(pr, u)
            return float(pr[ik:].sum())
        return rel

    def rel(A):
        d = {0.0: 1.0}
        for n, w, p in zip(A, W, R):
            if n == 0:
                continue
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
                    wu = aw + tw
                    nd[wu] = nd.get(wu, 0.0) + ap * tp
            d = nd
        return sum(pr for wt, pr in d.items() if wt >= K - 1e-9)
    return rel


def gfill(n, budget, costs, order):
    m = len(costs)
    mc = min(costs)
    A = [0] * m
    money = 0.0
    for s in range(n):
        rem = n - s - 1
        for j in order:
            if money + costs[j] + rem * mc <= budget + 1e-9:
                A[j] += 1
                money += costs[j]
                break
        else:
            j = min(range(m), key=lambda x: costs[x])
            A[j] += 1
            money += costs[j]
    return A, money


def solve(n, k, budget, W, C, R, tbs):
    m = len(C)
    deadline = time.perf_counter() + tbs
    rel = make_rel(W, R, k)

    # --- Diverse candidate generation ---
    cands = []
    keys = [
        lambda j: -(W[j] * R[j] / C[j]),
        lambda j: -(W[j] / C[j]),
        lambda j: -(W[j] * R[j]),
        lambda j: -R[j],
        lambda j: -(W[j] * R[j] ** 2 / C[j]),
    ]
    for key in keys:
        o = sorted(range(m), key=key)
        a, _ = gfill(n, budget, C, o)
        cands.append(a)
    # Single-type focus
    for f in range(m):
        o = [f] + [j for j in range(m) if j != f]
        a, _ = gfill(n, budget, C, o)
        cands.append(a)
    # Two-type focus
    for i in range(m):
        for j in range(i + 1, m):
            o = [i, j] + [x for x in range(m) if x != i and x != j]
            a, _ = gfill(n, budget, C, o)
            cands.append(a)

    ba = max(cands, key=rel)
    br = rel(ba)
    cur = list(ba)
    cr = br
    cm = sum(c * a for c, a in zip(C, cur))

    rng = random.Random(12345)

    # --- Iterated local search with multi-unit swaps ---
    while time.perf_counter() < deadline:
        # Local search phase
        imp = True
        while imp and time.perf_counter() < deadline:
            imp = False
            for t in range(1, min(6, n)):
                if imp:
                    break
                for a in range(m):
                    if imp or cur[a] < t:
                        continue
                    for b in range(m):
                        if b == a:
                            continue
                        cd = C[b] * t - C[a] * t
                        if cm + cd > budget + 1e-9:
                            continue
                        cur[a] -= t
                        cur[b] += t
                        r = rel(cur)
                        if r > cr + 1e-12:
                            cr = r
                            cm += cd
                            imp = True
                            break
                        else:
                            cur[a] += t
                            cur[b] -= t

        # Accept/reject
        if cr > br + 1e-12:
            br = cr
            ba = list(cur)
        else:
            cur = list(ba)
            cr = br
            cm = sum(c * a for c, a in zip(C, cur))

        # Perturbation: kick the solution to escape local optimum
        for _ in range(rng.randint(1, 3)):
            a = rng.randint(0, m - 1)
            b = rng.randint(0, m - 1)
            if a == b or cur[a] == 0:
                continue
            t = rng.randint(1, min(3, cur[a]))
            cd = C[b] * t - C[a] * t
            if cm + cd > budget + 1e-9:
                if cm + C[b] - C[a] <= budget + 1e-9:
                    t = 1
                    cd = C[b] - C[a]
                else:
                    continue
            cur[a] -= t
            cur[b] += t
            cm += cd
        cr = rel(cur)

    return ba


def main():
    path, out = sys.argv[1], sys.argv[2]
    tbs = float(os.environ.get("KOFN_TIME", "40"))
    n, k, budget, W, C, R = parse(path)
    alloc = solve(n, k, budget, W, C, R, tbs)
    rel = make_rel(W, R, k)
    rv = rel(alloc)
    with open(out, "w") as f:
        f.write(f"R {rv:.6f}\n")
        f.write(" ".join(map(str, alloc)) + "\n")


if __name__ == "__main__":
    main()