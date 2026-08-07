"""Exhaustive branch-and-bound ile KANITLI maksimum cap set (P4.2).

Kucuk n'de F_3^n uzayinda maksimum cap set'i (3-AP'siz en buyuk alt kume)
bagimsiz olarak bulur. Bu, evaluator (objective.py) cap-set kontrolunun
dogrulugu icin ground-truth kanitidir (kofn'deki Faz C karsiligii):
a(n) klasik olarak bilindiginden, enumerate onu birebir bulmalidir.

Cap = 3-uniform hypergraph'ta maksimum bagimsiz kume: bir noktayi secince,
onu secili herhangi ciftle birlestiren 3-AP'nin ucuncu noktasi artik
eklenemez (blocked). B&B sabit nokta sirasiyla: her noktayi "sec / secme"
dallarinda gezer; current_size + kalan <= best ise buda.

n<=3'te saniyeler icinde (27 nokta). n>=4 (81+ nokta) yavas olabilir;
o durumda enumerate yalnizca alt sinir (feasible cap) verir, optimallik
iddia ETMEZ (CLAUDE.md §5 P4.2: n>=4 optimallik literature aittir).

Determinizm (garanti edilen): sabit nokta sirasi (0..3^n-1) + ilk
bulunan max-size cap korunur (esitlik halinde `best` guncellenmez).
Boylece ayni instance + ayni Python -> ayni cap (tekrarlanabilirlik).
NOT: ciktinin leksikografik en kucuk oldugu GARANTI EDILMEZ — kod ilk
rastlanan max-size cap'i dondurur (greedy baslangic + B&B bulus sirasi).

CLI: python -m problems.capset.enumerate <instance.cap>
"""

import itertools
import time

from .objective import penalty_scale  # noqa: F401  (tutarluluk icin)


def _all_vectors(n):
    """F_3^n tum vektorleri, sabit leksikografik sirada (0..3^n-1)."""
    return list(itertools.product((0, 1, 2), repeat=n))


def _third(x, y, n):
    """x,y ile 3-AP olusturan ucuncu nokta: z = -(x+y) mod 3."""
    return tuple((-(x[i] + y[i])) % 3 for i in range(n))


def _build_lines(n):
    """Her nokta -> onunla bir cift olusturan (diger, ucuncu) ciftleri.

    lines_of[i] = [(j,k), ...]: {i,j,k} bir line (i<j<k sirali degil,
    ham). Bu, i secilince j de secili ise k blocked olur (ve perm).
    """
    V = _all_vectors(n)
    idx = {v: i for i, v in enumerate(V)}
    m = len(V)
    lines_of = [[] for _ in range(m)]
    seen = set()
    for i in range(m):
        for j in range(i + 1, m):
            k = idx[_third(V[i], V[j], n)]
            if k == i or k == j:
                continue  # degenerat (F_3'te olmaz ama guvenlik)
            line = tuple(sorted((i, j, k)))
            if line in seen:
                continue
            seen.add(line)
            a, b, c = line
            lines_of[a].append((b, c))
            lines_of[b].append((a, c))
            lines_of[c].append((a, b))
    return V, lines_of


def _greedy_initial(n, V, lines_of):
    """Hizli greedy cap -> baslangic best'i (pruning'i guclendir)."""
    m = len(V)
    chosen = [False] * m
    blocked = [False] * m
    cap = []
    for i in range(m):
        if blocked[i]:
            continue
        chosen[i] = True
        cap.append(i)
        # i eklendi: i ile bir ciftte olan ve secili olan varsa ucuncu blocked
        for (b, c) in lines_of[i]:
            if chosen[b] and not blocked[c]:
                blocked[c] = True
            elif chosen[c] and not blocked[b]:
                blocked[b] = True
        blocked[i] = True  # tekrar engelle
    return cap


def enumerate_optimum(instance, time_limit_s=None):
    """F_3^instance.dimension'da maksimum cap set'i B&B ile bulur.

    Donus: {"size", "cap" (vektor listesi), "node_count", "time_ms",
            "proven" (bool)}. proven=False ise yalnizca alt sinir (time_limit
            veya n>=4 kapsam dişi) — optimallik iddia edilmez.
    """
    n = instance.dimension
    t0 = time.perf_counter()
    V, lines_of = _build_lines(n)
    m = len(V)

    # Baslangic best'i greedy ile (pruning guclensin)
    init_cap = _greedy_initial(n, V, lines_of)
    best = {"size": len(init_cap), "cap": init_cap[:]}
    node_count = [0]
    timed_out = [False]

    # B&B: nokta sirasiyla sec/secme. blocked[i] = i su an eklenemez.
    chosen = [False] * m
    blocked = [False] * m
    current = []

    def bb(i, size):
        node_count[0] += 1
        # zaman siniri: her 16384 dugumde kontrol; asildiysa tum arama durur
        # (flag ile — return yalnizca dali bitirir, global flag butununu).
        if (node_count[0] & 0x3FFF) == 0:
            if time_limit_s is not None and time.perf_counter() - t0 > time_limit_s:
                timed_out[0] = True
        if timed_out[0]:
            return

        # budama: elimizdeki + kalan tum noktalar bile best'i gecemezse
        if size + (m - i) <= best["size"]:
            return

        if i == m:
            if size > best["size"]:
                best["size"] = size
                best["cap"] = current[:]
            return

        # Dal 1: i'yi SEC (blocked degilse)
        if not blocked[i]:
            newly_blocked = []
            for (b, c) in lines_of[i]:
                if chosen[b]:
                    if not blocked[c]:
                        blocked[c] = True
                        newly_blocked.append(c)
                elif chosen[c]:
                    if not blocked[b]:
                        blocked[b] = True
                        newly_blocked.append(b)
            chosen[i] = True
            current.append(i)
            bb(i + 1, size + 1)
            current.pop()
            chosen[i] = False
            for x in newly_blocked:
                blocked[x] = False
            if timed_out[0]:
                return

        # Dal 2: i'yi SECME
        bb(i + 1, size)

    # n>=4 icin zaman siniri (CLAUDE.md: dakikalari asmasin; alt sinir kabul).
    # time_limit_s parametresi verilmediyse varsayilan: n<=3 -> sinirsiz (kanit),
    # n>=4 -> kisa (alt sinir; tam kanit dakikalar alir).
    limit = time_limit_s
    if limit is None:
        limit = None if n <= 3 else 10.0
    if limit is not None:
        time_limit_s = limit
    bb(0, 0)

    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    cap_vectors = [V[i] for i in best["cap"]]

    return {
        "size": best["size"],
        "cap": cap_vectors,
        "node_count": node_count[0],
        "time_ms": elapsed_ms,
        "proven": not timed_out[0],
    }


def main(argv):
    from .io import parse_instance

    inst = parse_instance(argv[1])
    r = enumerate_optimum(inst)
    tag = "KANITLI" if r["proven"] else "ALT SINIR (zaman/tamamlanmadi)"
    print(f"instance        : {inst.name} (n={inst.dimension})")
    print(f"optimum cap     : |S| = {r['size']}  [{tag}]")
    print(f"sure            : {r['time_ms']} ms  (B&B dugum: {r['node_count']})")
    if r["proven"] and inst.dimension <= 3:
        print(f"literatur a(n)  : a({inst.dimension}) = {r['size']} (birebir)")
    elif not r["proven"]:
        print(f"not: n>=4 B&B yavas; bu bir alt sinir, optimallik literature aittir")


if __name__ == "__main__":
    import sys

    main(sys.argv)
