"""Bagimsiz tahsis dogrulayicisi — weighted k-out-of-n:G, cok tipli sistem.

Ozkut & Tutuncu (2025, C&IE 210, 111513) problem 4.3.2 icin: verilen bir
tahsisin (n_1..n_M) fizibilitesini ve sistem guvenilirligini R = P(calisan
birimlerin toplam agirligi >= K) TAM RASYONEL ARITMETIKLE (fractions.Fraction)
hesaplar. Kayan nokta hatasi tasimaz; ayni girdide her platformda ayni
sonucu verir.

Yalnizca Python standart kutuphanesi kullanir (Python >= 3.9). Kurulum
gerektirmez.

Kullanim:
  1) Tek tahsis dogrulama:
     python verify_kofn.py <instance.kofn> "n1 n2 ... nM"
     python verify_kofn.py <instance.kofn> <tahsis_dosyasi.txt>
  2) Sertifika dosyasinin tamamini denetleme (paketteki sertifikalar.csv):
     python verify_kofn.py --csv sertifikalar.csv [--instances instances]
  3) Kucuk instance'ta KANITLI optimum (exhaustive brute-force tarama —
     makaledeki yaklasimin karsiligi; tum tahsisler tek tek denenir):
     python verify_kofn.py --enum <instance.kofn>

Cikis kodu: 0 = fizibil / tum satirlar dogru; 1 = en az bir uyumsuzluk;
2 = girdi hatasi.

.kofn dosya bicimi: satir tabanli metin, '#' yorum baslatir. Basliklar:
NAME <ad>, M <tip sayisi>, N <pozisyon sayisi>, K <esik>, BUDGET <butce>,
ardindan tam M satir "TYPE <j 1..M> <agirlik> <maliyet> <guvenilirlik>".
"""

import csv
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


@dataclass(frozen=True)
class Instance:
    name: str
    m: int
    n_total: int
    k: Fraction
    budget: Fraction
    weights: tuple
    costs: tuple
    reliabilities: tuple


def parse_instance(path) -> Instance:
    headers, types = {}, {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        key = parts[0].upper()
        if key == "TYPE":
            if len(parts) != 5:
                raise ValueError(f"TYPE satiri 4 alan ister: {raw!r}")
            types[int(parts[1])] = tuple(Fraction(t) for t in parts[2:5])
        elif key in ("NAME", "M", "N", "K", "BUDGET"):
            headers[key] = parts[1]
        else:
            raise ValueError(f"bilinmeyen satir: {raw!r}")
    m = int(headers["M"])
    if sorted(types) != list(range(1, m + 1)):
        raise ValueError(f"TYPE satirlari 1..{m} olmali: {sorted(types)}")
    ts = [types[j] for j in range(1, m + 1)]
    return Instance(
        name=headers["NAME"], m=m, n_total=int(headers["N"]),
        k=Fraction(headers["K"]), budget=Fraction(headers["BUDGET"]),
        weights=tuple(t[0] for t in ts), costs=tuple(t[1] for t in ts),
        reliabilities=tuple(t[2] for t in ts))


def system_reliability(counts, instance) -> Fraction:
    """R = P(Σ ξ_j·N_j >= K), N_j ~ Binom(n_j, p_j) bagimsiz.

    Toplam agirlik dagiliminin birim birim konvolusyonu (DP). Tum ara
    degerler Fraction: sonuc kesindir.
    """
    dist = {Fraction(0): Fraction(1)}
    for j, nj in enumerate(counts):
        w, p = instance.weights[j], instance.reliabilities[j]
        q = 1 - p
        for _ in range(nj):
            new = {}
            for acc_w, acc_p in dist.items():
                new[acc_w] = new.get(acc_w, Fraction(0)) + acc_p * q
                wu = acc_w + w
                new[wu] = new.get(wu, Fraction(0)) + acc_p * p
            dist = new
    return sum(
        (pr for wt, pr in dist.items() if wt >= instance.k), Fraction(0))


def r12(fr) -> str:
    """Fraction -> 12 ondalik haneye dogru yuvarlanmis metin."""
    i = round(fr * 10**12)
    return f"{i // 10**12}.{i % 10**12:012d}"


def check(instance, counts) -> dict:
    """Fizibilite + kesin R. Sonuc: {feasible, violations, money, r}."""
    violations = []
    if len(counts) != instance.m:
        violations.append(
            f"tahsis {instance.m} deger istiyor, {len(counts)} geldi")
        return {"feasible": False, "violations": violations,
                "money": None, "r": None}
    if any(c < 0 for c in counts):
        violations.append("negatif adet var")
    total = sum(counts)
    if total != instance.n_total:
        violations.append(
            f"toplam adet {total} != N {instance.n_total}")
    money = sum(c * n for c, n in zip(instance.costs, counts))
    if money > instance.budget:
        violations.append(
            f"butce asimi: maliyet {money} > BUDGET {instance.budget}")
    r = None
    if not any(c < 0 for c in counts):
        r = system_reliability(tuple(counts), instance)
    return {"feasible": not violations, "violations": violations,
            "money": money, "r": r}


def _compositions(total, parts):
    """total'in parts parcaya kompozisyonlari, leksikografik sirada."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, parts - 1):
            yield (first,) + rest


def enumerate_optimum(instance, limit=2_000_000) -> dict:
    """Exhaustive brute-force ile KANITLI optimum (kucuk instance'lar).

    Tum C(N+M-1, M-1) tahsisi tek tek dener; butceye uyanlarin R'sini
    kesin aritmetikle hesaplar. Beraberlik kurali (deterministik):
    en yuksek R -> en dusuk maliyet -> leksikografik en kucuk tahsis.
    Kompozisyon sayisi limit'i asarsa ValueError (buyuk instance'larda
    brute-force zaten amac disi; oralarda sertifika karsilastirmalidir).
    """
    from math import comb
    n_comp = comb(instance.n_total + instance.m - 1, instance.m - 1)
    if n_comp > limit:
        raise ValueError(
            f"{n_comp} kompozisyon > limit {limit}: bu instance brute-force"
            f" icin buyuk (enumerasyon yalniz kucuk katman icindir)")
    best = None  # (r, -money, neg-lex icin alloc karsilastirmasi asagida)
    feasible_count = 0
    for alloc in _compositions(instance.n_total, instance.m):
        money = sum(c * n for c, n in zip(instance.costs, alloc))
        if money > instance.budget:
            continue
        feasible_count += 1
        r = system_reliability(alloc, instance)
        if best is None or r > best["r"] or (
                r == best["r"] and
                (money, alloc) < (best["money"], best["alloc"])):
            best = {"r": r, "money": money, "alloc": alloc}
    if best is None:
        raise ValueError(f"{instance.name}: fizibil tahsis yok")
    best["feasible_count"] = feasible_count
    return best


def _parse_alloc_arg(arg, m):
    p = Path(arg)
    text = p.read_text(encoding="utf-8") if p.is_file() else arg
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if parts[0] == "R" and len(parts) == 2:
            continue  # cozucu beyan satiri; yok say
        return tuple(int(t) for t in parts)
    raise ValueError("tahsis satiri bulunamadi")


def verify_csv(csv_path, instances_dir):
    """sertifikalar.csv'nin her satirini yeniden hesaplayarak denetler."""
    results = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row["instance"]
            inst_file = Path(instances_dir) / f"{name}.kofn"
            if not inst_file.is_file():
                results.append({"instance": name, "ok": False,
                                "detail": f"dosya yok: {inst_file}"})
                continue
            inst = parse_instance(inst_file)
            counts = tuple(int(t) for t in row["allocation"].split())
            v = check(inst, counts)
            if not v["feasible"]:
                results.append({"instance": name, "ok": False,
                                "detail": "; ".join(v["violations"])})
                continue
            got = r12(v["r"])
            ok = got == row["R_exact_12dp"].strip()
            detail = ("dogrulandi" if ok else
                      f"R uyusmuyor: beyan {row['R_exact_12dp']}, "
                      f"hesap {got}")
            results.append({"instance": name, "ok": ok, "detail": detail})
    return results


def main(argv):
    if len(argv) >= 2 and argv[1] == "--enum":
        if len(argv) != 3:
            print(__doc__)
            return 2
        inst = parse_instance(argv[2])
        try:
            opt = enumerate_optimum(inst)
        except ValueError as e:
            print(f"HATA: {e}")
            return 2
        print(f"instance: {inst.name} (N={inst.n_total}, M={inst.m}, "
              f"K={inst.k}, BUDGET={inst.budget})")
        print(f"kanitli optimum tahsis: "
              f"{' '.join(str(c) for c in opt['alloc'])}")
        print(f"maliyet: {opt['money']} (BUDGET {inst.budget})")
        print(f"R (kesin, 12 hane): {r12(opt['r'])}")
        print(f"taranan fizibil tahsis: {opt['feasible_count']}")
        return 0

    if len(argv) >= 2 and argv[1] == "--csv":
        csv_path = argv[2]
        inst_dir = "instances"
        if "--instances" in argv:
            inst_dir = argv[argv.index("--instances") + 1]
        results = verify_csv(csv_path, inst_dir)
        for r in results:
            print(f"{'OK  ' if r['ok'] else 'FAIL'} {r['instance']}: "
                  f"{r['detail']}")
        n_ok = sum(1 for r in results if r["ok"])
        print(f"\n{n_ok}/{len(results)} satir dogrulandi")
        return 0 if n_ok == len(results) else 1

    if len(argv) != 3:
        print(__doc__)
        return 2
    inst = parse_instance(argv[1])
    counts = _parse_alloc_arg(argv[2], inst.m)
    v = check(inst, counts)
    print(f"instance: {inst.name} (N={inst.n_total}, M={inst.m}, "
          f"K={inst.k}, BUDGET={inst.budget})")
    print(f"tahsis: {' '.join(str(c) for c in counts)}")
    if v["money"] is not None:
        print(f"maliyet: {v['money']} (BUDGET {inst.budget})")
    if v["feasible"]:
        print("fizibilite: OK")
    else:
        print("fizibilite: IHLAL — " + "; ".join(v["violations"]))
    if v["r"] is not None:
        print(f"R (kesin, 12 hane): {r12(v['r'])}")
    return 0 if v["feasible"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
