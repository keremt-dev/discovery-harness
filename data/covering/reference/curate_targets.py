"""LJCR arsivinden evrim hedefi hucre kurasyonu (covering designs).

Kaynak: sources/coverdata.json (dmgordo/LJCR, arsiv donmus 2026-03-01).
Sema: {"C(v,k,t)": {"size": int, "low_bd": int, "imps": [[size, method,
submitter, timestamp], ...]}} — imps'te en yeni kayit basta olmak zorunda
degil; eskilik icin MAX timestamp alinir.

Kurasyon kriterleri (CLAUDE.md §3 kurasyon ruhu + skill §3):
  1. gap = size - low_bd >= 1     (gap=0 -> kanitli optimal, hedef OLAMAZ;
                                   ancak bekci/pozitif kontrol olabilir)
  2. C(v,t) <= VERIFY_CAP         (kesin dogrulama Python'da saniyeler
                                   icinde kalsin — evaluator butcesi)
  3. size <= SIZE_CAP             (cozum ciktisi yonetilebilir; LLM'in
                                   uretecegi kod makul surede insa etsin)
  4. sweet bandi: 3<=t<=5, 20<=v<=60, >=10 yil iyilestirilmemis
                                   (t=2 literatur-yogun; Tao gozlemi:
                                   basari literatur yogunluguyla ters)

Cikti: targets.csv (tum hucreler, bayraklarla) + stdout ozet.
Schoenheim alt siniri TAM tamsayi aritmetigiyle hesaplanir ve arsivin
low_bd'siyle capraz kontrol edilir (enstruman kalibrasyonunun ilk adimi).
"""

import csv
import json
import math
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "sources" / "coverdata.json"
OUT = HERE / "targets.csv"

# Arsiv 2026-03-01'de donduruldu; eskilik bu sabit referansla hesaplanir
# (script deterministik kalsin diye bugunun tarihi degil).
REF_DATE = datetime(2026, 3, 1)

VERIFY_CAP = 10_000_000  # C(v,t) ustu: kesin dogrulama pahali -> hedef disi
SIZE_CAP = 2000          # blok sayisi ustu: cozum uretimi/IO hantal


def ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def schoenheim(v: int, k: int, t: int) -> int:
    """L(v,k,t) = ceil(v/k * L(v-1,k-1,t-1)), L(v,k,1) = ceil(v/k).

    Tam tamsayi aritmetigi; float yok.
    """
    if t == 1:
        return ceil_div(v, k)
    return ceil_div(v * schoenheim(v - 1, k - 1, t - 1), k)


def parse_name(name: str):
    inner = name[name.index("(") + 1:name.index(")")]
    v, k, t = (int(x) for x in inner.split(","))
    return v, k, t


def parse_ts(ts: str):
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    anomalies = {"low_bd_lt_schoenheim": [], "size_lt_low_bd": []}

    for name, cell in data.items():
        v, k, t = parse_name(name)
        size = int(cell["size"])
        low_bd = int(cell["low_bd"])
        sch = schoenheim(v, k, t)
        cvt = math.comb(v, t)
        ckt = math.comb(k, t)

        stamps = [parse_ts(imp[3]) for imp in cell.get("imps", [])]
        stamps = [s for s in stamps if s is not None]
        last_imp = max(stamps) if stamps else None
        years_stale = (
            (REF_DATE - last_imp).days / 365.25 if last_imp else None
        )

        if low_bd < sch:
            anomalies["low_bd_lt_schoenheim"].append(name)
        if size < low_bd:
            anomalies["size_lt_low_bd"].append(name)

        gap = size - low_bd
        eligible = gap >= 1 and cvt <= VERIFY_CAP and size <= SIZE_CAP
        sweet = (
            eligible
            and 3 <= t <= 5
            and 20 <= v <= 60
            and years_stale is not None
            and years_stale >= 10
        )
        rows.append({
            "v": v, "k": k, "t": t,
            "size": size, "low_bd": low_bd, "schoenheim": sch,
            "gap": gap, "gap_schoenheim": size - sch,
            "C(v,t)": cvt, "C(k,t)": ckt,
            "last_improvement": last_imp.date().isoformat() if last_imp else "",
            "years_stale": round(years_stale, 1) if years_stale is not None else "",
            "n_improvements": len(stamps),
            "eligible": int(eligible), "sweet": int(sweet),
        })

    rows.sort(key=lambda r: (
        -r["sweet"], -r["eligible"],
        -(r["years_stale"] if r["years_stale"] != "" else -1),
        -r["gap"],
    ))

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n_opt = sum(1 for r in rows if r["gap"] == 0)
    n_eli = sum(1 for r in rows if r["eligible"])
    n_sweet = sum(1 for r in rows if r["sweet"])
    print(f"toplam hucre           : {len(rows)}")
    print(f"kanitli optimal (gap=0): {n_opt}")
    print(f"eligible (hedef aday)  : {n_eli}")
    print(f"sweet band             : {n_sweet}")
    print(f"anomali low_bd<Schonheim: {len(anomalies['low_bd_lt_schoenheim'])}")
    print(f"anomali size<low_bd     : {len(anomalies['size_lt_low_bd'])}")
    if anomalies["size_lt_low_bd"]:
        print("  !!", anomalies["size_lt_low_bd"][:10])

    print("\n--- sweet band ilk 25 (eskilik sirali) ---")
    hdr = ["v", "k", "t", "size", "low_bd", "schoenheim", "gap",
           "C(v,t)", "last_improvement", "years_stale", "n_improvements"]
    print("  ".join(f"{h:>16}" if h == "last_improvement" else f"{h:>10}"
                    for h in hdr))
    for r in [r for r in rows if r["sweet"]][:25]:
        print("  ".join(
            f"{str(r[h]):>16}" if h == "last_improvement" else f"{str(r[h]):>10}"
            for h in hdr))


if __name__ == "__main__":
    main()
