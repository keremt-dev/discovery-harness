"""P4 tohum solver'i — evrim dongusunun baslangic genomu (cap set).

Strateji (CLAUDE.md §5 P4.3): RASTGELE-GREEDY kurulum (karistirilmis
sirada uyumluysa ekle; eklenince 3-AP olusturan vektorleri blocked yap)
+ extend (greedy sonrasi eklenebilen kaldiysa ekle) + SWAP hill-climb
(1 vektor cikar -> blocked kismen ac -> 2+ ekle, net kazanç) +
random-restart (anytime). FunSearch skeleton (cap_set.ipynb cell 2)
mantigi; P4.0'da dogruladigimiz O(|S|^2) blocking kurali.

Kasitli zayiflatma (strawman) YOK — meşru en iyi saf greedy + local
search. n=8'de ~250-350 cap (gradyan bol; FunSearch 512, evrim icin yer
var). Cebirsel Hill cap doubling EKLENMEDI — evrim bunu kesfetmeli
(FunSearch boyle yapti); tohum'a gommek keşif alanini daraltir + §0.5
sizinti riski.

Kendi kendine yeten tek dosya: evaluator koduna bagimliligi yoktur. Cap
kontrolu tamsayi aritmetigiyle (z=-(x+y) mod 3).

Sozlesme (kofn/cvrp seed_solver deseni):
    python seed_solver.py <instance.cap> <cikti.txt> [--seed N]

CAPSET_SEED_TIME_S (env, default 10): anytime sure butcesi. Atomik
yazim (os.replace) -> timeout aninda yarim satir kalmaz (§3).
"""

import argparse
import itertools
import os
import random
import time


def parse_instance_file(path):
    """Instance dosyasini okur; yalnizca dimension dondurur (kendi kendine yeten)."""
    n = None
    for raw in open(path, encoding="utf-8"):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if parts[0].lower() == "dimension":
            n = int(parts[1])
    if n is None:
        raise ValueError("dimension bulunamadi")
    return n


def _powers(n):
    return [3 ** (n - 1 - i) for i in range(n)]


def _code(v, pw):
    return sum(c * p for c, p in zip(v, pw))


def _third(x, y, n):
    return tuple((-(x[i] + y[i])) % 3 for i in range(n))


def _greedy_construct(n, order, pw):
    """Rastgele-greedy: 'order' sirasiyla ekle; blocked vektoru atla.

    Bir vektor eklenince, onunla ve her secili ciftle 3-AP olusturan
    ucuncu vektoru (z=-(x+y) mod 3) blocked yap. (cap |S|) dondurur;
    blocked set'i de (swap icin).
    """
    blocked = set()
    cap = []
    for v in order:
        cv = _code(v, pw)
        if cv in blocked:
            continue
        cap.append(v)
        for u in cap[:-1]:
            z = _third(u, v, n)
            blocked.add(_code(z, pw))
        blocked.add(cv)
    return cap, blocked


def _extend(n, cap, blocked, pw, all_vecs):
    """Greedy sonrasi hala eklenebilen varsa ekle (cap'i maksimize)."""
    cap = list(cap)
    blocked = set(blocked)
    added = True
    while added:
        added = False
        for v in all_vecs:
            cv = _code(v, pw)
            if cv in blocked or v in cap:
                continue
            cap.append(v)
            for u in cap[:-1]:
                z = _third(u, v, n)
                blocked.add(_code(z, pw))
            blocked.add(cv)
            added = True
            break
    return cap, blocked


def _swap_hillclimb(n, cap, pw, all_vecs, deadline):
    """1-cikar / k-ekle takas: bir vektoru cikar, acilan alanla 2+ ekle.

    Net kazanç (yeni eklenenler > cikarilan 1) varsa uygula. Klasik cap
    set local search. Sure bütçesi içinde.
    """
    improved = True
    while improved and time.perf_counter() < deadline:
        improved = False
        for remove_idx in range(len(cap)):
            if time.perf_counter() >= deadline:
                break
            # cikar
            removed = cap[remove_idx]
            trial = cap[:remove_idx] + cap[remove_idx + 1:]
            # yeniden blocked hesapla (trial cap'e gore)
            cap_set = set(trial)
            blocked = set()
            for x in trial:
                for y in trial:
                    if x < y:
                        blocked.add(_code(_third(x, y, n), pw))
                blocked.add(_code(x, pw))
            # removed serbest mi + baska kac vektor eklenebilir?
            candidates = [v for v in all_vecs
                          if _code(v, pw) not in blocked and v not in cap_set]
            # removed'u da aday say (geri eklenme ihtimali)
            if removed in candidates:
                candidates.remove(removed)
            # greedy ekle (extend mantigi)
            new_cap = list(trial)
            new_blocked = set(blocked)
            for v in candidates:
                cv = _code(v, pw)
                if cv in new_blocked or v in new_cap:
                    continue
                new_cap.append(v)
                for u in new_cap[:-1]:
                    z = _third(u, v, n)
                    new_blocked.add(_code(z, pw))
                new_blocked.add(cv)
            if len(new_cap) > len(cap):
                cap = new_cap
                improved = True
                break
    return cap


def solve(instance, time_budget_s, seed=0, on_improve=None):
    """Anytime tohum cap set uretir.

    instance: capset.io.Instance (dimension kullanilir).
    time_budget_s: yumusak sure butcesi (her restart sonrasi kontrol).
    seed: deterministik RNG tohumu (reproducibility).
    on_improve: opsiyonel callback `on_improve(cap)`; en iyi cap guncellendiginde
        cagrilir. main() bunu atomik cikti yazimi icin kullanir (anytime: ilk
        yazim ilk restart'in greedy+extend'inden HEMEN sonra, hill-climb oncesi).
    Donus: cap vektor listesi (tuple'lar, n uzunlugunda {0,1,2}).

    Anytime akisi (her restart):
      1. greedy_construct + extend -> iyilesme varsa on_improve (ERKEN yazim).
      2. swap hill-climb (kalan surenin ~%30'u) -> iyilesme varsa on_improve.
    Boylece hill-climb bütçeyi tüketse bile cikti dosyasi erken olusur; runner
    timeout'u (DISCOVERY_SOLVER_TIMEOUT_S) tohum bütçesinin altina duserse bile
    gecerli cozum vardir (Görev 1 düzeltmesi).
    """
    n = instance.dimension
    pw = _powers(n)
    all_vecs = list(itertools.product((0, 1, 2), repeat=n))

    deadline = time.perf_counter() + time_budget_s
    rng = random.Random(seed)
    best = []

    def _consider(cap):
        nonlocal best
        if len(cap) > len(best):
            best = cap
            if on_improve is not None:
                on_improve(best)

    restart = 0
    while time.perf_counter() < deadline:
        order = list(all_vecs)
        rng.shuffle(order)
        cap, blocked = _greedy_construct(n, order, pw)
        cap, blocked = _extend(n, cap, blocked, pw, all_vecs)
        _consider(cap)  # ERKEN yazim: greedy+extend sonrasi, hill-climb oncesi
        # hill-climb: kalan surenin ~%30'u (tek yerde — main() ile tutarli).
        remaining = deadline - time.perf_counter()
        hc_deadline = time.perf_counter() + max(0.05, remaining * 0.3)
        cap = _swap_hillclimb(n, cap, pw, all_vecs, hc_deadline)
        _consider(cap)  # hill-climb sonrasi yeniden yaz
        restart += 1
        if restart > 100000:  # kucuk n'de doygunlukta sonsuz dongu korumasi
            break

    if not best:  # guvenlik: en azindan tek vektor
        best = [all_vecs[0]]
        if on_improve is not None:
            on_improve(best)
    return best


def format_solution(cap):
    """Cozum metnini kur: '# size K' beyani + bitisik {0,1,2} satirlari."""
    lines = [f"# size {len(cap)}"]
    for v in cap:
        lines.append("".join(str(c) for c in v))
    return "\n".join(lines) + "\n"


def _atomic_write(path, text):
    """Gecici dosyaya yaz + os.replace ile atomik degistir (anytime §3)."""
    tmp = str(path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, str(path))


def main(argv=None):
    parser = argparse.ArgumentParser(description="cap set tohum solver")
    parser.add_argument("instance")
    parser.add_argument("output")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    n = parse_instance_file(args.instance)
    time_budget_s = float(os.environ.get("CAPSET_SEED_TIME_S", "10"))

    # anytime + atomik: solve() on_improve callback'inde her iyilesmde yaz.
    # Ilk yazim ilk restart'in greedy+extend'inden hemen (hill-climb oncesi)
    # gelir -> runner timeout'u tohum bütçesinin altina duserse bile gecerli
    # cozum vardir (Görev 1).
    from types import SimpleNamespace
    instance = SimpleNamespace(dimension=n)

    def _write(cap):
        _atomic_write(args.output, format_solution(cap))

    solve(instance, time_budget_s, seed=args.seed, on_improve=_write)


if __name__ == "__main__":
    main()
