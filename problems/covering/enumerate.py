"""Exhaustive arama ile KANITLI minimum covering (P5 Faz C).

Kucuk (v,k,t) hucrelerinde minimum blok sayisini bagimsiz olarak kanitlar:
iterative deepening — m = Schoenheim(v,k,t)'den baslayarak her derinlikte
DFS; ilk basarili m = kanitli optimum (daha kucuk tum m'ler fiilen
curutulmus, Schoenheim alti teoremle imkansiz). Bu, evaluator'un
(objective.py) dogrulugu icin ground-truth kanitidir: enumerate'in
optimumu, arsivin kanitli hucreleriyle ve evaluate_text ile birebir
ortusmek zorundadir (kofn/capset Faz C karsiligi).

DFS dallanmasi: leksikografik EN KUCUK kapsanmamis t-altkumeyi sec;
onu kapsayan bloklar (leksikografik sirali) uzerinden dallan. Budama:
|B| + ceil(|kapsanmamis| / C(k,t)) > m ise geri don. Her gecerli covering
"ilk kapsanmamis altkumesini kapsayan bir blok icerir" oldugu icin arama
TAM'dir (hicbir cozum kacmaz).

Determinizm (garanti): sabit dallanma sirasi -> bulunan optimal cozum
leksikografik-ilk cozumdur; ayni instance + ayni Python = ayni bloklar.
Tie-break: obj (min blok) -> leksikografik ilk (skill Faz C kurali).

Kapsam: C(v,k) ve C(v,t) <= ENUM_CAP olan hucreler. Buyuk hucrelerde
(hedef instance'lar dahil) kanit uretmez — proven=False, blocks=None
(buyuk hucre tohum/evrim isidir, Faz D/E; capset n>=4 deseni).

CLI: python -m problems.covering.enumerate <instance.cover>
"""

import math
import time
from itertools import combinations

from .spec import schoenheim

# Kanit aramasina girilecek hucre siniri: aday blok sayisi C(v,k) ve
# t-altkume sayisi C(v,t) bu esigi asarsa kanit kapsam disi (Faz D isi).
ENUM_CAP = 100_000


def _greedy_cover(all_blocks, cover_of, total):
    """Leksikografik-deterministik greedy: en cok yeni altkume kapsayan
    (esitlikte leksikografik ilk) blogu sec. Ust sinir / fallback cozumu."""
    uncovered = set()
    for tsets in cover_of:
        uncovered.update(tsets)
    chosen = []
    while uncovered:
        best_i, best_gain = None, 0
        for i, tsets in enumerate(cover_of):
            gain = len(uncovered & tsets)
            if gain > best_gain:
                best_i, best_gain = i, gain
        if best_i is None:
            break  # olmamali: her altkume en az bir blokta
        chosen.append(best_i)
        uncovered -= cover_of[best_i]
    return chosen


def enumerate_optimum(instance, time_limit_s=None):
    """Minimum covering'i iterative deepening DFS ile kanitlar.

    Donus: {"size", "blocks" (sirali tuple listesi | None), "lower_bound",
            "node_count", "time_ms", "proven"}.
    proven=False iki durumda: kapsam disi (blocks=None) ya da zaman siniri
    (blocks = greedy ust sinir cozumu; optimallik iddia edilmez).
    """
    v, k, t = instance.v, instance.k, instance.t
    t0 = time.perf_counter()
    lb = schoenheim(v, k, t)
    total = math.comb(v, t)
    n_blocks = math.comb(v, k)

    if n_blocks > ENUM_CAP or total > ENUM_CAP:
        return {
            "size": None, "blocks": None, "lower_bound": lb,
            "node_count": 0,
            "time_ms": int((time.perf_counter() - t0) * 1000),
            "proven": False,
        }

    all_blocks = list(combinations(range(1, v + 1), k))  # leksikografik
    cover_of = [frozenset(combinations(b, t)) for b in all_blocks]
    all_tsets = list(combinations(range(1, v + 1), t))   # leksikografik
    per_block = math.comb(k, t)

    # pivot t-altkumeyi kapsayan blok indeksleri (leksikografik sirali)
    blocks_with = {ts: [] for ts in all_tsets}
    for i, tsets in enumerate(cover_of):
        for ts in tsets:
            blocks_with[ts].append(i)

    greedy = _greedy_cover(all_blocks, cover_of, total)
    ub = len(greedy)

    node_count = [0]
    timed_out = [False]
    chosen = []

    def dfs(uncovered, limit):
        node_count[0] += 1
        if (node_count[0] & 0xFFF) == 0 and time_limit_s is not None:
            if time.perf_counter() - t0 > time_limit_s:
                timed_out[0] = True
        if timed_out[0]:
            return False
        if not uncovered:
            return True
        need = -(-len(uncovered) // per_block)  # ceil
        if len(chosen) + need > limit:
            return False
        pivot = min(uncovered)  # leksikografik en kucuk kapsanmamis
        for i in blocks_with[pivot]:
            chosen.append(i)
            if dfs(uncovered - cover_of[i], limit):
                return True
            chosen.pop()
            if timed_out[0]:
                return False
        return False

    full = frozenset(all_tsets)
    for m in range(lb, ub + 1):
        if time_limit_s is not None and \
                time.perf_counter() - t0 > time_limit_s:
            timed_out[0] = True
            break
        chosen.clear()
        if dfs(set(full), m):
            blocks = [all_blocks[i] for i in chosen]
            return {
                "size": m, "blocks": blocks, "lower_bound": lb,
                "node_count": node_count[0],
                "time_ms": int((time.perf_counter() - t0) * 1000),
                "proven": True,
            }
        if timed_out[0]:
            break

    # zaman siniri: greedy ust siniri feasible cozum olarak dondur
    blocks = [all_blocks[i] for i in greedy]
    return {
        "size": ub, "blocks": blocks, "lower_bound": lb,
        "node_count": node_count[0],
        "time_ms": int((time.perf_counter() - t0) * 1000),
        "proven": False,
    }


def solution_text(result) -> str:
    """Enumerate ciktisini cozum metni formatina cevirir (evaluator kaniti)."""
    return "\n".join(" ".join(str(x) for x in b) for b in result["blocks"])


def main(argv):
    from .io import parse_instance

    inst = parse_instance(argv[1])
    r = enumerate_optimum(inst)
    print(f"instance   : {inst.name} (v={inst.v}, k={inst.k}, t={inst.t})")
    print(f"Schoenheim : {r['lower_bound']}")
    if r["blocks"] is None:
        print(f"kanit      : KAPSAM DISI (C(v,k) ya da C(v,t) > {ENUM_CAP}) — "
              "buyuk hucre tohum/evrim isidir (Faz D/E)")
        return
    tag = "KANITLI OPTIMUM" if r["proven"] else "UST SINIR (zaman siniri)"
    print(f"sonuc      : {r['size']} blok  [{tag}]")
    print(f"sure       : {r['time_ms']} ms  (DFS dugum: {r['node_count']})")
    print(solution_text(r))


if __name__ == "__main__":
    import sys

    main(sys.argv)
