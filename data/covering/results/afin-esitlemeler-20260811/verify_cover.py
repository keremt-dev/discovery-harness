#!/usr/bin/env python3
"""Bagimsiz covering dogrulayici — YALNIZCA Python stdlib (sertifika deseni).

Bu dosya, birlikte geldigi solution.txt'nin C(28,9,3) icin gecerli bir
covering design oldugunu HERHANGI bir ek kod/kutuphane olmadan dogrular.
Aliciya guven gerekmez: dogrulama saf sayimdir.

    python verify_cover.py 28 9 3 solution.txt

Cikti: blok sayisi + kapsanmayan 3-altkume sayisi (0 olmali) + SONUC.
Genel kullanim: herhangi bir (v,k,t) ve cozum dosyasi verilebilir.
Cozum formati: '#' yorumlari serbest; her satir k adet FARKLI tamsayi
(1..v), bosluk ayracli; bloklar kume olarak okunur, tekrar blok HATA.
"""

import sys
from itertools import combinations


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    v, k, t = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    blocks = []
    with open(sys.argv[4], encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            nums = [int(x) for x in line.split()]
            if len(nums) != k or len(set(nums)) != k or \
                    any(not (1 <= x <= v) for x in nums):
                print(f"HATA satir {lineno}: gecersiz blok {nums}")
                return 1
            blocks.append(tuple(sorted(nums)))

    if len(set(blocks)) != len(blocks):
        print(f"HATA: {len(blocks) - len(set(blocks))} tekrar blok")
        return 1

    covered = set()
    for b in blocks:
        covered.update(combinations(b, t))

    total = 0
    uncovered = 0
    first_uncovered = None
    for c in combinations(range(1, v + 1), t):
        total += 1
        if c not in covered:
            uncovered += 1
            if first_uncovered is None:
                first_uncovered = c

    print(f"v={v} k={k} t={t}")
    print(f"blok sayisi        : {len(blocks)}")
    print(f"t-altkume          : {total}")
    print(f"kapsanmayan        : {uncovered}")
    if first_uncovered:
        print(f"ilk kapsanmayan    : {first_uncovered}")
    if uncovered == 0:
        print(f"SONUC: GECERLI COVERING — C({v},{k},{t}) <= {len(blocks)}")
        return 0
    print("SONUC: GECERSIZ (kapsanmayan altkume var)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
