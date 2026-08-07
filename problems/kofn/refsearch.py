"""Headroom turnusolu: cok baslangicli, cok birimli referans arama.

Amac: "tohumun ustunde ulasilabilir alan (headroom) var mi?" sorusunu
OPTIMUM BILMEDEN olcmek. headroom = ref_R - tohum_R:
- headroom ~ 0  -> instance, mevcut yerel aramayla cozulmus; EVRIM ICIN COP
  (2026-08-04 dersi: gen-n120-m6-s2'de 50 iterasyon duz cizgiydi cunku
  tohum zaten tavandaydi).
- headroom > esik -> tohumun kacamadigi ama ULASILABILIR bolge var; evrimin
  kesfedecegi gercek alan.

Referans arama optimum iddiasi TASIMAZ (alt sinirdir); bu yuzden kurasyon
kriteri olarak kullanilir, rekor iddiasi olarak degil.

Deterministik: sabit rng_seed + sabit baslangic sirasi + kesin-iyilesme
kabulu. Zaman butcesi YOKTUR (makine yuku sonucu degistirmesin).

CLI: python -m problems.kofn.refsearch <instance.kofn>
"""

import random

from .seed_solver import construct, reliability

MOVE_SIZES = (1, 2, 4, 8)


def _local_search(alloc, money, weights, costs, rels, k, budget,
                  move_sizes=MOVE_SIZES):
    """Transfer hamleleriyle best-improvement hill-climb (deterministik).

    move_sizes=(1,) tekil-takas = idealize tohum davranisi (sure limitsiz);
    varsayilan cok-birimli set = referans arama.
    """
    m = len(alloc)
    best_r = reliability(alloc, weights, rels, k)
    while True:
        best_move = None
        for a in range(m):
            for b in range(m):
                if a == b:
                    continue
                for t in move_sizes:
                    if alloc[a] < t:
                        continue
                    delta = (costs[b] - costs[a]) * t
                    if money + delta > budget + 1e-9:
                        continue
                    alloc[a] -= t
                    alloc[b] += t
                    r = reliability(alloc, weights, rels, k)
                    alloc[a] += t
                    alloc[b] -= t
                    if r > best_r + 1e-12 and (
                            best_move is None or r > best_move[0]):
                        best_move = (r, a, b, t)
        if best_move is None:
            return alloc, best_r
        best_r, a, b, t = best_move
        alloc[a] -= t
        alloc[b] += t
        money += (costs[b] - costs[a]) * t


def _random_feasible(n, costs, budget, rng):
    """Rastgele kompozisyon + maliyet onarimi (pahalidan en ucuza kaydir)."""
    m = len(costs)
    cuts = sorted(rng.randint(0, n) for _ in range(m - 1))
    alloc, prev = [], 0
    for c in cuts + [n]:
        alloc.append(c - prev)
        prev = c
    cheapest = costs.index(min(costs))
    money = sum(c * x for c, x in zip(costs, alloc))
    while money > budget:
        movable = [j for j in range(m) if alloc[j] > 0 and j != cheapest]
        if not movable:
            return None
        j = max(movable, key=lambda jj: costs[jj])
        if costs[j] <= costs[cheapest]:
            return None  # onarim ilerlemiyor
        alloc[j] -= 1
        alloc[cheapest] += 1
        money += costs[cheapest] - costs[j]
    return alloc, money


def reference_search(instance, starts=32, rng_seed=0) -> dict:
    n, m = instance.n_total, instance.m
    weights = [float(w) for w in instance.weights]
    costs = [float(c) for c in instance.costs]
    rels = [float(p) for p in instance.reliabilities]
    k, budget = float(instance.k), float(instance.budget)
    rng = random.Random(rng_seed)

    start_allocs = []
    a0, m0 = construct(n, budget, weights, costs, rels)
    start_allocs.append((list(a0), m0))          # 1) oran-greedy (tohum)
    for j in range(m):                            # 2) tek-tip tahsisler
        money = costs[j] * n
        if money <= budget:
            al = [0] * m
            al[j] = n
            start_allocs.append((al, money))
    tries = 0                                     # 3) rastgele fizibil
    while len(start_allocs) < starts and tries < starts * 20:
        tries += 1
        cand = _random_feasible(n, costs, budget, rng)
        if cand:
            start_allocs.append(cand)

    best_alloc, best_r = None, -1.0
    for al, money in start_allocs:
        al, r = _local_search(list(al), money, weights, costs, rels, k, budget)
        if r > best_r + 1e-15:  # kesin iyilesme; esitlikte ilk bulunan kalir
            best_alloc, best_r = list(al), r
    return {
        "reliability": best_r,
        "alloc": tuple(best_alloc),
        "starts": len(start_allocs),
    }


def idealized_seed(instance):
    """Sure limitsiz tohum: oran-greedy kurulum + TEKIL-takas hill-climb.

    Gercek tohum (seed_solver) zaman butcelidir; buradaki idealize hali
    deterministiktir ve tohumun ulasabileceginin ust siniridir -> headroom
    olcumu muhafazakar kalir (gercek headroom en az bu kadardir).
    """
    weights = [float(w) for w in instance.weights]
    costs = [float(c) for c in instance.costs]
    rels = [float(p) for p in instance.reliabilities]
    alloc, money = construct(instance.n_total, float(instance.budget),
                             weights, costs, rels)
    alloc, r = _local_search(list(alloc), money, weights, costs, rels,
                             float(instance.k), float(instance.budget),
                             move_sizes=(1,))
    return {"reliability": r, "alloc": tuple(alloc)}


def headroom(instance, starts=32, rng_seed=0) -> dict:
    seed = idealized_seed(instance)
    ref = reference_search(instance, starts=starts, rng_seed=rng_seed)
    return {
        "seed_r": seed["reliability"],
        "ref_r": ref["reliability"],
        "headroom": ref["reliability"] - seed["reliability"],
        "seed_alloc": seed["alloc"],
        "ref_alloc": ref["alloc"],
    }


def main(argv):
    from .io import parse_instance

    inst = parse_instance(argv[1])
    h = headroom(inst)
    print(f"instance : {inst.name}")
    print(f"tohum R  : {h['seed_r']:.6f}  alloc={h['seed_alloc']}")
    print(f"ref R    : {h['ref_r']:.6f}  alloc={h['ref_alloc']}")
    print(f"headroom : {h['headroom']:.6f}")


if __name__ == "__main__":
    import sys

    main(sys.argv)
