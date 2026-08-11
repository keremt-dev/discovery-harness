"""LJCR arsivinin satir satir yeniden hesabi (enstruman kalibrasyonu).

kofn'daki verify_fyffe / verify_ozkut2025 deseninin covering karsiligi:
yayinlanmis tabloya KORU KORUNE guvenme, kesin aritmetikle yeniden hesapla.
Burada dogrulanabilir olan uc invariant + bir literatur teoremi:

  I1. schoenheim(v,k,t) <= low_bd   (Schoenheim standart alt sinir;
      arsivin alt siniri ondan asagi olamaz — olursa ya bizim formul
      ya arsiv bozuk -> SERT HATA)
  I2. low_bd <= size                (alt sinir bilinen en iyi cozumu
      asamaz -> SERT HATA)
  I3. imps tarihcesi: zaman sirasina dizildiginde size'lar artmamali
      (bir "iyilestirme" onceki kayittan buyuk olamaz). Ihlal = veri
      hijyeni bulgusu; SERT DEGIL (arsivde eski toplu yuklemeler var),
      raporlanir.
  T1. Fort-Hedlund 1958: C(v,3,2) = Schoenheim siniri (tum v >= 3).
      k=3,t=2 hucrelerinde size == schoenheim beklenir; sapma ya arsiv
      hatasi ya formul hatasi -> SERT HATA. (Bu, iki bagimsiz kaynagin
      birbirini kalibre etmesi: teorem <-> arsiv <-> bizim formul.)

Cikis kodu: 0 = tum sert invariantlar gecti; 1 = sert ihlal var.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent))  # repo koku

from problems.covering.spec import schoenheim  # noqa: E402

SOURCE = HERE / "sources" / "coverdata.json"


def parse_name(name):
    inner = name[name.index("(") + 1:name.index(")")]
    v, k, t = (int(x) for x in inner.split(","))
    return v, k, t


def parse_ts(ts):
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    hard = []
    soft = []
    fh_checked = 0

    for name, cell in data.items():
        v, k, t = parse_name(name)
        size, low_bd = int(cell["size"]), int(cell["low_bd"])
        sch = schoenheim(v, k, t)

        if sch > low_bd:
            hard.append(f"I1 {name}: schoenheim={sch} > low_bd={low_bd}")
        if low_bd > size:
            hard.append(f"I2 {name}: low_bd={low_bd} > size={size}")

        imps = []
        for imp in cell.get("imps", []):
            ts = parse_ts(imp[3])
            try:
                s = int(imp[0])
            except (ValueError, TypeError):
                soft.append(f"I3 {name}: sayisal olmayan imp size {imp[0]!r}")
                continue
            if ts is not None:
                imps.append((ts, s))
        imps.sort()
        for (t0, s0), (t1, s1) in zip(imps, imps[1:]):
            if s1 > s0:
                soft.append(
                    f"I3 {name}: {t0.date()}→{t1.date()} size {s0}→{s1} ARTMIS")
        if imps and imps[-1][1] != size:
            soft.append(
                f"I3 {name}: son imp size {imps[-1][1]} != guncel size {size}")

        if k == 3 and t == 2:
            fh_checked += 1
            if size != sch:
                hard.append(
                    f"T1 {name}: size={size} != schoenheim={sch}"
                    " (Fort-Hedlund ihlali)")

    print(f"hucre sayisi              : {len(data)}")
    print(f"Fort-Hedlund kontrolu     : {fh_checked} hucre (k=3,t=2)")
    print(f"SERT ihlal (I1/I2/T1)     : {len(hard)}")
    print(f"yumusak bulgu (I3 hijyen) : {len(soft)}")
    for h in hard[:20]:
        print("  !!", h)
    if soft:
        print("ilk 10 yumusak bulgu:")
        for s in soft[:10]:
            print("   -", s)

    if hard:
        print("\nSONUC: SERT IHLAL VAR — enstruman ya arsiv sorunu, dongu kurulmadan once cozulmeli.")
        return 1
    print("\nSONUC: tum sert invariantlar gecti (I1, I2, T1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
