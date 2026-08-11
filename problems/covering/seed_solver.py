"""P5 tohum solver'i — evrim dongusunun baslangic genomu (covering design).

Strateji: GREEDY kurulum (leksikografik en kucuk kapsanmamis t-altkumeden
basla; blogu, ORNEKLENMIS aday kumesinden en cok yeni altkume kazandiran
elemanla buyut) + REDUNDANCY REMOVAL (tum altkumeleri baska bloklarca da
kapsanan bloklari at) + RUIN-AND-RECREATE yerel arama (rastgele 1-3 blok
sok, greedy tamir et, esit/daha iyi ise kabul) + anytime restart.

Neden ornekleme: tam max-gain taramasi (tum v aday x C(k-1,t-1) altkume)
buyuk hucrede (C(32,8,4) ~800 blok) Python'da tek greedy gecisini onlarca
saniyeye cikarir; SAMPLE_CANDIDATES adaylik rastgele panel kaliteyi az,
hizi 5-10x etkiler. Kasitli zayiflatma DEGIL — mesru hiz/kalite dengesi;
evrim daha iyi kurulum/tamir stratejilerini kesfetmeli (§0.5: arsiv
degerleri buraya SIZDIRILMAZ).

Kendi kendine yeten tek dosya (stdlib-only); evaluator koduna bagimlilik
yok. Anytime + atomik yazim (os.replace): ILK yazim greedy gecisi
SIRASINDA kismi kapsama olarak baslar (PARTIAL_WRITE_EVERY blokta bir) —
runner timeout'u erken duserse bile gradyanli (uncovered sayili) cikti
kalir; tam kapsama saglaninca ve her iyilesmede yeniden yazilir.

Sozlesme (kofn/capset seed_solver deseni):
    python seed_solver.py <instance.cover> <cikti.txt> [--seed N]

COVERING_SEED_TIME_S (env, default 10): anytime sure butcesi.
"""

import argparse
import os
import random
import time
from itertools import combinations

SAMPLE_CANDIDATES = 8      # blok buyutmede degerlendirilecek aday sayisi
PARTIAL_WRITE_EVERY = 50   # greedy sirasinda kismi yazim araligi (blok)
RUIN_MAX = 3               # ruin-and-recreate'te sokulecek blok ust siniri


def parse_instance_file(path):
    """Instance dosyasini okur; (v, k, t) dondurur (kendi kendine yeten)."""
    vals = {}
    for raw in open(path, encoding="utf-8"):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if parts[0].lower() in ("v", "k", "t"):
            vals[parts[0].lower()] = int(parts[1])
    if set(vals) != {"v", "k", "t"}:
        raise ValueError("v/k/t basliklari eksik")
    return vals["v"], vals["k"], vals["t"]


def _grow_block(v, k, t, start, uncovered, rng):
    """Bir t-altkumeden k-blok buyut: her adimda SAMPLE_CANDIDATES rastgele
    aday arasindan en cok yeni (kapsanmamis) altkume kazandirani sec."""
    block = list(start)
    in_block = set(block)
    while len(block) < k:
        pool = [x for x in range(1, v + 1) if x not in in_block]
        if len(pool) > SAMPLE_CANDIDATES:
            pool = rng.sample(pool, SAMPLE_CANDIDATES)
        best_x, best_gain = None, -1
        for x in pool:
            gain = 0
            for sub in combinations(sorted(block), t - 1):
                cand = tuple(sorted(sub + (x,)))
                if cand in uncovered:
                    gain += 1
            if gain > best_gain:
                best_x, best_gain = x, gain
        block.append(best_x)
        in_block.add(best_x)
    return tuple(sorted(block))


def _greedy_cover(v, k, t, uncovered, rng, on_partial=None):
    """uncovered kalmayana dek blok uret. on_partial(blocks) araliklarla
    cagirilir (anytime kismi yazim)."""
    blocks = []
    while uncovered:
        pivot = min(uncovered)  # leksikografik: deterministik cati
        block = _grow_block(v, k, t, pivot, uncovered, rng)
        blocks.append(block)
        for sub in combinations(block, t):
            uncovered.discard(sub)
        if on_partial is not None and \
                len(blocks) % PARTIAL_WRITE_EVERY == 0:
            on_partial(blocks)
    return blocks


def _coverage_counts(blocks, t):
    counts = {}
    for b in blocks:
        for sub in combinations(b, t):
            counts[sub] = counts.get(sub, 0) + 1
    return counts


def _remove_redundant(blocks, t, counts, rng):
    """Tum t-altkumeleri >=2 kez kapsanan bloklari (rastgele sirayla) at."""
    order = list(range(len(blocks)))
    rng.shuffle(order)
    alive = [True] * len(blocks)
    for i in order:
        b = blocks[i]
        if all(counts[sub] >= 2 for sub in combinations(b, t)):
            for sub in combinations(b, t):
                counts[sub] -= 1
            alive[i] = False
    return [b for i, b in enumerate(blocks) if alive[i]]


def solve(v, k, t, time_budget_s, seed=0, on_improve=None):
    """Anytime tohum covering uretir; blok listesi (sirali tuple) dondurur.

    on_improve(blocks, feasible) her yazim noktasinda cagirilir: kismi
    (feasible=False, greedy sirasinda) ve tam/iyilesme (feasible=True).
    """
    rng = random.Random(seed)
    deadline = time.perf_counter() + time_budget_s
    all_tsets = set(combinations(range(1, v + 1), t))

    def partial_cb(blocks):
        if on_improve is not None:
            on_improve(blocks, False)

    # 1) ilk greedy + redundancy removal
    blocks = _greedy_cover(v, k, t, set(all_tsets), rng, on_partial=partial_cb)
    counts = _coverage_counts(blocks, t)
    blocks = _remove_redundant(blocks, t, counts, rng)
    best = list(blocks)
    if on_improve is not None:
        on_improve(best, True)

    # 2) ruin-and-recreate: esit/daha iyi kabul (drift), iyide yaz
    current = list(best)
    while time.perf_counter() < deadline and len(current) > 1:
        r = rng.randint(1, min(RUIN_MAX, len(current) - 1))
        victims = set(rng.sample(range(len(current)), r))
        kept = [b for i, b in enumerate(current) if i not in victims]
        counts = _coverage_counts(kept, t)
        holes = {ts for ts in all_tsets if ts not in counts}
        repaired = kept + _greedy_cover(v, k, t, holes, rng)
        counts = _coverage_counts(repaired, t)
        repaired = _remove_redundant(repaired, t, counts, rng)
        if len(repaired) <= len(current):
            current = repaired
            if len(current) < len(best):
                best = list(current)
                if on_improve is not None:
                    on_improve(best, True)
    return best


def format_solution(blocks):
    lines = [f"# size {len(blocks)}"]
    for b in blocks:
        lines.append(" ".join(str(x) for x in b))
    return "\n".join(lines) + "\n"


def _atomic_write(path, text):
    tmp = str(path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, str(path))


def main(argv=None):
    parser = argparse.ArgumentParser(description="covering tohum solver")
    parser.add_argument("instance")
    parser.add_argument("output")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    v, k, t = parse_instance_file(args.instance)
    time_budget_s = float(os.environ.get("COVERING_SEED_TIME_S", "10"))

    def _write(blocks, feasible):
        _atomic_write(args.output, format_solution(blocks))

    solve(v, k, t, time_budget_s, seed=args.seed, on_improve=_write)


if __name__ == "__main__":
    main()
