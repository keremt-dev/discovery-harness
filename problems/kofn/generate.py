"""Tohumlu instance ureteci (Faz D).

Tasarim ilkeleri (docs/bilimsel-iddia-plani.md §5, p1-problem-tanimi.md §1):
- Deterministik: ayni (n, m, seed) daima ayni dosyayi uretir.
- Fizibilite garantisi: hepsi-en-ucuz tahsis daima butceye sigar.
- Doyumsuz K bandi: K, butce altinda ULASILABILIR maksimum agirligin
  (w_reach) %70-95'inden secilir -> problem ne umutsuz (R_opt=0) ne doymus
  (R_opt~1'de beraberlik copu).
- Tamsayi agirlik/maliyet: agirlik-DP'nin durum sayisini sinirli tutar.

CLI: python -m problems.kofn.generate <n> <m> <seed> [cikti.kofn]
"""

import random
from statistics import mean

from .seed_solver import construct, weight_distribution


def _quantile_k(n, types, budget, rng):
    """K'yi, oran-greedy kurulumun agirlik dagiliminin sagkalim egrisi
    uzerinde hedef q ~ U(0.25, 0.75) noktasina koyar.

    Sabit-oran band (%70-95 x maks agirlik) buyuk n'de doyuma gidiyordu:
    buyuk sayilar yasasiyla toplam agirligin gorece varyansi kuculur ve
    K ortalamanin cok altinda kalir (R_opt ~ 1). Kuantil yerlesimi her
    n'de yapisal doyumsuzluk garantiler: kurulum tahsisinin R'si ~ q olur.
    """
    weights = [float(w) for w, _, _ in types]
    costs = [float(c) for _, c, _ in types]
    rels = [float(p) for _, _, p in types]
    alloc, _ = construct(n, float(budget), weights, costs, rels)
    dist = weight_distribution(alloc, weights, rels)
    q = rng.uniform(0.25, 0.75)
    best_w, best_diff = None, None
    survival = 1.0
    for w in sorted(dist):  # artan agirlik; S(w) = P(W >= w) azalir
        diff = abs(survival - q)
        if best_diff is None or diff < best_diff:
            best_w, best_diff = w, diff
        survival -= dist[w]
    return max(1, int(round(best_w)))


def _max_weight_alloc(n, types, budget):
    """Butce altinda tek-birim yukseltmelerle ulasilabilir maks-AGIRLIK
    tahsisi (hepsi-en-ucuz'dan agirlik kazancli takaslarla)."""
    costs = [c for _, c, _ in types]
    alloc = [0] * len(types)
    alloc[costs.index(min(costs))] = n
    money = sum(c * x for c, x in zip(costs, alloc))
    while True:
        best = None
        for a in range(len(types)):
            if alloc[a] == 0:
                continue
            for b in range(len(types)):
                gain_w = types[b][0] - types[a][0]
                if b == a or gain_w <= 0:
                    continue
                if money + costs[b] - costs[a] > budget:
                    continue
                if best is None or gain_w > best[0]:
                    best = (gain_w, a, b)
        if best is None:
            return alloc
        _, a, b = best
        alloc[a] -= 1
        alloc[b] += 1
        money += costs[b] - costs[a]


def _survival_quantile(alloc, types, q):
    """alloc'un agirlik dagiliminda S(w)=P(W>=w) ~ q olan agirlik."""
    weights = [float(w) for w, _, _ in types]
    rels = [float(p) for _, _, p in types]
    dist = weight_distribution(alloc, weights, rels)
    best_w, best_diff = None, None
    survival = 1.0
    for w in sorted(dist):
        diff = abs(survival - q)
        if best_diff is None or diff < best_diff:
            best_w, best_diff = w, diff
        survival -= dist[w]
    return max(1, int(round(best_w)))


def generate_instance(n, m, seed, profile="standart") -> str:
    rng = random.Random(seed)
    if profile == "standart":
        types = []
        for _ in range(m):
            w = rng.randint(1, 9)
            p = round(rng.uniform(0.85, 0.99), 2)
            # maliyet kaliteyle (agirlik x guvenilirlik) iliskili + gurultu
            c = max(1, round(w * p * rng.uniform(0.6, 1.6)))
            types.append((w, c, p))
        costs = [c for _, c, _ in types]
        budget = max(n * min(costs),
                     round(n * mean(costs) * rng.uniform(0.6, 0.9)))
        k = _quantile_k(n, types, budget, rng)
    elif profile == "sert":
        # Oran-aldatmali plato profili (2026-08-05; docs/faz-e-gradyan.md):
        # hafif tipler cok ucuz (w*p/c orani en iyi -> tohum bunlari sever),
        # agir tipler super-lineer pahali ama K'ya ulasmak icin sart. K,
        # maks-AGIRLIK tahsisinin kuantilinde -> oran-greedy'nin tahsisi
        # R~0 bolgesinde kalir; tekil takas yolu olu bolgeden gecer.
        types = []
        for _ in range(m):
            w = rng.randint(1, 12)
            p = round(rng.uniform(0.85, 0.99), 2)
            c = max(1, round((w ** 1.5) * p * rng.uniform(0.8, 1.2)))
            types.append((w, c, p))
        costs = [c for _, c, _ in types]
        # dar butce: en-ucuz dolumun az ustu -> yalniz birkac agir birim alinabilir
        budget = max(n * min(costs),
                     round(n * min(costs) * rng.uniform(1.2, 1.8)))
        heavy = _max_weight_alloc(n, types, budget)
        k = _survival_quantile(heavy, types, rng.uniform(0.3, 0.7))
    elif profile == "router":
        # Benchmark v1, Iz-2 (2026-08-05): makalenin router senaryosu
        # rejimi (§4.3 ornekleri, xi=1..3 / p=0.92-0.97 civari) olceklenmis:
        # kucuk tamsayi agirliklar (veri hizi), yuksek guvenilirlik,
        # maliyet kaliteyle iliskili. Aldatma YOK — gercekci benchmark.
        types = []
        for _ in range(m):
            w = rng.randint(1, 5)
            p = round(rng.uniform(0.90, 0.99), 2)
            c = max(1, round(w * rng.uniform(0.8, 1.3)))
            types.append((w, c, p))
        costs = [c for _, c, _ in types]
        budget = max(n * min(costs),
                     round(n * mean(costs) * rng.uniform(0.7, 0.95)))
        k = _quantile_k(n, types, budget, rng)
    elif profile == "enerji":
        # Benchmark v1, Iz-2: enerji senaryosu — kapasite agirliklari
        # birbirine yakin ama farkli (makaledeki 2/1.9/2.1 oraninin x10
        # tamsayi olcegi: 15..25), guvenilirlik bandi genis (yenilenebilir
        # vs termik), maliyet kapasite+kaliteyle iliskili.
        types = []
        for _ in range(m):
            w = rng.randint(15, 25)
            p = round(rng.uniform(0.75, 0.97), 2)
            c = max(1, round(w * p * rng.uniform(0.7, 1.4) / 2))
            types.append((w, c, p))
        costs = [c for _, c, _ in types]
        budget = max(n * min(costs),
                     round(n * mean(costs) * rng.uniform(0.7, 0.95)))
        k = _quantile_k(n, types, budget, rng)
    else:
        raise ValueError(f"bilinmeyen profil: {profile!r}")

    tag = "" if profile == "standart" else f"-{profile}"
    lines = [
        f"# uretec: problems/kofn/generate.py  (n={n}, m={m}, seed={seed},"
        f" profil={profile})",
        f"NAME gen{tag}-n{n}-m{m}-s{seed}",
        f"M {m}",
        f"N {n}",
        f"K {k}",
        f"BUDGET {budget}",
    ]
    for j, (w, c, p) in enumerate(types, 1):
        lines.append(f"TYPE {j} {w} {c} {p}")
    return "\n".join(lines) + "\n"


def main(argv):
    # kullanim: generate <n> <m> <seed> [cikti.kofn] [profil]
    n, m, seed = int(argv[1]), int(argv[2]), int(argv[3])
    profile = argv[5] if len(argv) > 5 else "standart"
    text = generate_instance(n, m, seed, profile=profile)
    if len(argv) > 4:
        with open(argv[4], "w", encoding="utf-8") as f:
            f.write(text)
        print(f"yazildi: {argv[4]}")
    else:
        print(text, end="")


if __name__ == "__main__":
    import sys

    main(sys.argv)
