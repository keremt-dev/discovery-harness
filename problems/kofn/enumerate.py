"""Exhaustive enumeration ile KANITLI optimum (Faz C ground truth).

Kucuk instance'larda tum tahsisleri (N'nin M parcaya kompozisyonlari)
sayar, butceye uyanlarin R'sini evaluator'un KENDI objective'iyle
(objective.system_reliability, tam Fraction) hesaplar ve optimumu dondurur.
Boylece "evaluator'un optimumu = enumeration optimumu" kaniti kurulur —
cvrp-discovery'de imkansiz olan enstruman dogrulugu kaniti (CLAUDE.md Faz C).

Beraberlik kurali (deterministik, tekrarlanabilirlik icin): en yuksek R,
sonra en dusuk maliyet, sonra leksikografik en kucuk tahsis.

Karmasiklik: C(N+M-1, M-1) tahsis x tahsis basi R hesabi. Yalnizca kucuk
n/M icindir; buyuk instance'larda zaten amac enumeration'in OLMEDIGI yerde
sezgiseli olcmektir (docs/bilimsel-iddia-plani.md §3).

CLI: python -m problems.kofn.enumerate <instance.kofn>
"""

from .objective import system_reliability


def _compositions(total, parts):
    """total'in parts parcaya kompozisyonlari, leksikografik sirada."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, parts - 1):
            yield (first,) + rest


def enumerate_optimum(instance) -> dict:
    """Kanitli optimumu dondurur; hic fizibil tahsis yoksa ValueError."""
    best_r = None
    best_money = None
    best_alloc = None
    feasible_count = 0
    tie_count = 0

    for alloc in _compositions(instance.n_total, instance.m):
        money = sum(c * n for c, n in zip(instance.costs, alloc))
        if money > instance.budget:
            continue
        feasible_count += 1
        r = system_reliability(alloc, instance)
        if best_r is None or r > best_r:
            best_r, best_money, best_alloc = r, money, alloc
            tie_count = 1
        elif r == best_r:
            tie_count += 1
            if (money, alloc) < (best_money, best_alloc):
                best_money, best_alloc = money, alloc

    if feasible_count == 0:
        raise ValueError(
            f"{instance.name}: fizibil tahsis yok "
            f"(N={instance.n_total} icin butce {instance.budget} yetmiyor)")

    return {
        "alloc": best_alloc,
        "reliability": best_r,
        "money_cost": best_money,
        "feasible_count": feasible_count,
        "tie_count": tie_count,
    }


def main(argv):
    from .io import parse_instance

    inst = parse_instance(argv[1])
    r = enumerate_optimum(inst)
    print(f"instance        : {inst.name}")
    print(f"kanitli optimum : {' '.join(map(str, r['alloc']))}")
    print(f"R (6 hane)      : {float(r['reliability']):.6f}")
    print(f"maliyet         : {float(r['money_cost'])} / {float(inst.budget)}")
    print(f"fizibil tahsis  : {r['feasible_count']} (beraberlik: {r['tie_count']})")


if __name__ == "__main__":
    import sys

    main(sys.argv)
