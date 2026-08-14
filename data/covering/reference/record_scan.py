"""Rekor-avi headroom taramasi (2026-08-13, B2 sonrasi).

Soru: arsivde hangi hucrelerde size - low_bd >= 1 boslugu var VE mevcut
makine (thinking620 genomu + odakli thinking-dilimi mekanizmasi) o
hucreye yapica yakin? Cikti, math.CO-tarafi rekor denemesinin hedef
listesidir.

Katmanlar (oncelik sirasiyla):
  FRONTIER : B2'de esitledigimiz hucre + gap>=1 -> zaten bilinen-en-iyi
             seviyesindeyiz; TEK blok dususu rekor eder. En degerli katman.
  NEAR     : B2'de +1/+2 kaldigimiz hucre + gap>=1 -> once esitleme
             (C(28,9,3)=56 emsali: odakli dilim), sonra itme.
  AFFINE   : afin konstruksiyon uygulanabilir (v=p^m, k=p^d, d>=t-1),
             gap>=1, B2 setinde YOK -> genom dogrudan calisir, esitleme
             beklenir; gap varsa itme denenir.
  CONSTR   : B2 negatif hucrelerinin (arsivin bizde olmayan konstruksiyonu
             oldugu kanitli) ayni-aile komsulari -> once konstruksiyonu
             yeniden kesfet (thinking-dilimi), sonra ailenin gap'li
             hucrelerini it.
  SEARCH   : kucuk, gap 1-2, arama-erimli hucreler (C(23,10,3)=24 emsali:
             konstruksiyonsuz evrilmis greedy+yerel arama esitledi).

Uyari (hedef-notlari.md #1 gecerli): gap>0 garanti headroom degildir —
alt sinir zayif olabilir. Bu tarama SIRALAMA uretir; iddia ancak fiili
dusus + bagimsiz dogrulama + canli skorbord kontroluyle yazilir.
"""

import csv
import json
import math
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "sources" / "coverdata.json"
OUT = HERE / "record_targets.csv"

REF_DATE = datetime(2026, 3, 1)  # arsiv dondurma tarihi (curate ile ayni)
VERIFY_CAP = 10_000_000
SIZE_CAP = 2000

# --- B2 benchmark sonuc kumesi (docs/benchmark-covering.md, 2026-08-13) ---
B2_TIED = {  # 22 esitleme (BEKCI + EGITIM + holdout hepsi dahil)
    (7, 3, 2), (13, 3, 2), (32, 8, 4), (8, 4, 3), (9, 3, 2), (16, 4, 3),
    (16, 8, 4), (25, 5, 2), (27, 3, 2), (27, 9, 3), (32, 4, 3),
    (32, 16, 5), (32, 17, 5), (49, 7, 2), (49, 8, 2), (64, 4, 3),
    (81, 3, 2), (81, 9, 3), (21, 10, 3), (20, 12, 4), (23, 10, 3),
    (25, 16, 4),
}
B2_NEAR = {(27, 10, 3): 1, (30, 12, 3): 1, (28, 9, 3): 2}  # +fark (en iyi seed)
B2_FAR = {(32, 18, 5): 43, (24, 6, 4): 263, (30, 9, 3): 25, (22, 15, 5): 7}


def ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def schoenheim(v: int, k: int, t: int) -> int:
    if t == 1:
        return ceil_div(v, k)
    return ceil_div(v * schoenheim(v - 1, k - 1, t - 1), k)


def prime_power(n: int):
    """n = p^m ise (p, m) dondur, degilse None."""
    if n < 2:
        return None
    for p in range(2, int(math.isqrt(n)) + 1):
        if n % p == 0:
            m = 0
            while n % p == 0:
                n //= p
                m += 1
            return (p, m) if n == 1 else None
    return (n, 1)


def gauss_binom(m: int, d: int, p: int) -> int:
    """[m choose d]_p — AG(m,p) icindeki d-flat yon sayisi carpani."""
    num = den = 1
    for i in range(d):
        num *= p ** (m - i) - 1
        den *= p ** (i + 1) - 1
    assert num % den == 0
    return num // den


def affine_info(v: int, k: int, t: int):
    """Afin uygulanabilirlik: v=p^m (m>=2), k=p^d (1<=d<m), d>=t-1.

    Dondurulen sayi: AG(m,p) tum d-flat'leri = p^(m-d) * [m choose d]_p.
    (thinking620'nin kesfettigi konstruksiyon ailesi; d>=t-1 kosulu her
    t-altkumesinin bir d-flat icinde kalmasini garantiler.)
    """
    pp = prime_power(v)
    if not pp or pp[1] < 2:
        return None
    p, m = pp
    kk = prime_power(k)
    if not kk or kk[0] != p:
        return None
    d = kk[1]
    if not (1 <= d < m and d >= t - 1):
        return None
    return p ** (m - d) * gauss_binom(m, d, p)


def parse_name(name: str):
    inner = name[name.index("(") + 1:name.index(")")]
    return tuple(int(x) for x in inner.split(","))


def parse_ts(ts: str):
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    for name, cell in data.items():
        v, k, t = parse_name(name)
        size, low_bd = int(cell["size"]), int(cell["low_bd"])
        gap = size - low_bd
        cvt = math.comb(v, t)
        stamps = [s for s in (parse_ts(i[3]) for i in cell.get("imps", []))
                  if s is not None]
        last = max(stamps) if stamps else None
        stale = (REF_DATE - last).days / 365.25 if last else None

        aff = affine_info(v, k, t)
        layers = []
        if (v, k, t) in B2_TIED and gap >= 1:
            layers.append("FRONTIER")
        if (v, k, t) in B2_NEAR and gap >= 1:
            layers.append("NEAR")
        if (v, k, t) in B2_FAR:
            layers.append("FAR-SELF")  # kendisi degil ailesi hedef
        verifiable = cvt <= VERIFY_CAP and size <= SIZE_CAP
        if (aff is not None and gap >= 1 and verifiable
                and (v, k, t) not in B2_TIED and (v, k, t) not in B2_NEAR):
            layers.append("AFFINE")
        # CONSTR: FAR hucreleriyle ayni (k,t) ailesi, yakin v, gap>=1
        for (fv, fk, ft) in B2_FAR:
            if (k, t) == (fk, ft) and v != fv and abs(v - fv) <= 8 \
                    and gap >= 1 and verifiable:
                layers.append(f"CONSTR({fv},{fk},{ft})")
        if (not layers and gap and 1 <= gap <= 2 and verifiable
                and 3 <= t <= 5 and 20 <= v <= 40 and size <= 60):
            layers.append("SEARCH")

        if layers:
            rows.append({
                "v": v, "k": k, "t": t, "layer": "+".join(layers),
                "size": size, "low_bd": low_bd,
                "schoenheim": schoenheim(v, k, t), "gap": gap,
                "affine_count": aff if aff is not None else "",
                "C(v,t)": cvt,
                "last_improvement": last.date().isoformat() if last else "",
                "years_stale": round(stale, 1) if stale is not None else "",
                "n_improvements": len(stamps),
            })

    prio = {"FRONTIER": 0, "NEAR": 1, "AFFINE": 2, "FAR-SELF": 3}
    rows.sort(key=lambda r: (
        prio.get(r["layer"].split("+")[0].split("(")[0], 4),
        -r["gap"],
    ))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    hdr = ["v", "k", "t", "layer", "size", "low_bd", "schoenheim", "gap",
           "affine_count", "C(v,t)", "years_stale", "n_improvements"]
    for layer in ["FRONTIER", "NEAR", "FAR-SELF", "AFFINE", "CONSTR", "SEARCH"]:
        sel = [r for r in rows if r["layer"].startswith(layer)
               or (layer == "CONSTR" and "CONSTR" in r["layer"])]
        if layer in ("AFFINE", "SEARCH", "CONSTR"):
            sel = sel[:15]
        if not sel:
            continue
        print(f"\n=== {layer} ({len(sel)} satir gosteriliyor) ===")
        print("  ".join(f"{h:>12}" for h in hdr))
        for r in sel:
            print("  ".join(f"{str(r[h]):>12}" for h in hdr))
    print(f"\ntoplam aday satir: {len(rows)} -> {OUT.name}")


if __name__ == "__main__":
    main()
