"""P1 tohum solver'i — evrim dongusunun baslangic genomu.

Strateji (CLAUDE.md Faz D): maliyet/fayda oranina gore GREEDY KURULUM
(her birim icin agirlik*guvenilirlik/maliyet orani en yuksek, butce
tamamlanabilirligini bozmayan tip) + tek birimlik takas hill-climb.
Bilerek naif — iyilestirme evrimin isi. (Salt "hepsi-en-ucuz" baslangic,
K yuksekken R=0 platosuna saplaniyordu: hicbir tekil takas esigi
gecemedigi icin gradyan yok. Oran-greedy kurulum bu platoyu asar.)
Kendi kendine yeter: evaluator koduna bagimliligi yoktur. Ic hesap
float'tir; kanonik deger daima evaluator tarafindan tam aritmetikle
yeniden hesaplanir.

Sozlesme (cvrp-discovery solver.py deseni):
    python seed_solver.py <instance.kofn> <cikti.txt>
Cikti: "R <tahmin>" beyan satiri (yalnizca durustluk sensoru) + M adet
tamsayidan olusan tahsis satiri.

KOFN_SEED_TIME_S (env, default 10): hill-climb icin yumusak sure butcesi —
buyuk instance'larda anytime davranis.
"""

import os
import sys
import time


def parse(path):
    headers, types = {}, {}
    for raw in open(path, encoding="utf-8"):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if parts[0] == "TYPE":
            types[int(parts[1])] = (
                float(parts[2]), float(parts[3]), float(parts[4]))
        else:
            headers[parts[0]] = parts[1]
    m = int(headers["M"])
    ts = [types[j] for j in range(1, m + 1)]
    return (int(headers["N"]), float(headers["K"]), float(headers["BUDGET"]),
            [t[0] for t in ts], [t[1] for t in ts], [t[2] for t in ts])


def weight_distribution(alloc, weights, rels):
    """Toplam agirlik dagilimi (agirlik -> olasilik), konvolusyon (float)."""
    dist = {0.0: 1.0}
    for nj, w, p in zip(alloc, weights, rels):
        q = 1.0 - p
        for _ in range(nj):
            new = {}
            for acc_w, acc_p in dist.items():
                new[acc_w] = new.get(acc_w, 0.0) + acc_p * q
                wu = acc_w + w
                new[wu] = new.get(wu, 0.0) + acc_p * p
            dist = new
    return dist


def reliability(alloc, weights, rels, k):
    """P(toplam agirlik >= k)."""
    dist = weight_distribution(alloc, weights, rels)
    return sum(pr for wt, pr in dist.items() if wt >= k - 1e-9)


def construct(n, budget, weights, costs, rels):
    """Oran-greedy kurulum: birim basina w*p/c orani en iyi tipi sec;
    kalan birimlerin en ucuz tiple tamamlanabilirligini daima koru."""
    m = len(costs)
    min_c = min(costs)
    order = sorted(range(m), key=lambda j: -(weights[j] * rels[j] / costs[j]))
    alloc = [0] * m
    money = 0.0
    for step in range(n):
        remaining = n - step - 1
        for j in order:
            if money + costs[j] + remaining * min_c <= budget:
                alloc[j] += 1
                money += costs[j]
                break
        else:  # hicbir tip sigmiyor (uretimde olmamali): en ucuza dus
            j = costs.index(min_c)
            alloc[j] += 1
            money += min_c
    return alloc, money


def solve(n, k, budget, weights, costs, rels, time_budget_s):
    m = len(costs)
    alloc, money = construct(n, budget, weights, costs, rels)
    if money > budget:
        return alloc  # fizibil tahsis yok; ihlali evaluator kodlar
    deadline = time.perf_counter() + time_budget_s
    best_r = reliability(alloc, weights, rels, k)
    while time.perf_counter() < deadline:
        best_move = None
        for a in range(m):
            if alloc[a] == 0:
                continue
            for b in range(m):
                if b == a or money + costs[b] - costs[a] > budget:
                    continue
                alloc[a] -= 1
                alloc[b] += 1
                r = reliability(alloc, weights, rels, k)
                alloc[a] += 1
                alloc[b] -= 1
                if r > best_r + 1e-12 and (
                        best_move is None or r > best_move[0]):
                    best_move = (r, a, b)
        if best_move is None:
            break
        best_r, a, b = best_move
        alloc[a] -= 1
        alloc[b] += 1
        money += costs[b] - costs[a]
    return alloc


def main():
    instance_path, out_path = sys.argv[1], sys.argv[2]
    time_budget_s = float(os.environ.get("KOFN_SEED_TIME_S", "10"))
    n, k, budget, weights, costs, rels = parse(instance_path)
    alloc = solve(n, k, budget, weights, costs, rels, time_budget_s)
    r = reliability(alloc, weights, rels, k)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"R {r:.6f}\n")
        f.write(" ".join(map(str, alloc)) + "\n")


if __name__ == "__main__":
    main()
