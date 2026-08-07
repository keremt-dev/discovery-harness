"""Instance parser: .kofn dosyasi -> Instance. Bozuk dosya RAISE eder.

(Cozum tarafinin aksine instance tarafinda hata sert olmalidir: bozuk
instance ile kosulan her sey coptur — sessizce devam edilmez.)
"""

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


class InstanceFormatError(Exception):
    """Instance dosyasi format sozlesmesini (spec.py) saglamiyor."""


@dataclass(frozen=True)
class Instance:
    name: str
    m: int
    n_total: int
    k: Fraction
    budget: Fraction
    weights: tuple    # ξ_j, j=1..M
    costs: tuple      # c_j
    reliabilities: tuple  # p_j


def _fraction(token, field):
    try:
        return Fraction(token)
    except (ValueError, ZeroDivisionError):
        raise InstanceFormatError(f"{field}: sayi cozumlenemedi: {token!r}")


def parse_instance(path) -> Instance:
    text = Path(path).read_text(encoding="utf-8")
    headers = {}
    types = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        key = parts[0].upper()
        if key == "TYPE":
            if len(parts) != 5:
                raise InstanceFormatError(f"TYPE satiri 4 alan ister: {raw!r}")
            idx = int(_fraction(parts[1], "TYPE idx"))
            types[idx] = (
                _fraction(parts[2], "TYPE agirlik"),
                _fraction(parts[3], "TYPE maliyet"),
                _fraction(parts[4], "TYPE guvenilirlik"),
            )
        elif key in ("NAME", "M", "N", "K", "BUDGET"):
            if len(parts) != 2:
                raise InstanceFormatError(f"{key} tek deger ister: {raw!r}")
            headers[key] = parts[1]
        else:
            raise InstanceFormatError(f"bilinmeyen satir: {raw!r}")

    for req in ("NAME", "M", "N", "K", "BUDGET"):
        if req not in headers:
            raise InstanceFormatError(f"zorunlu baslik eksik: {req}")

    m = int(_fraction(headers["M"], "M"))
    n_total = int(_fraction(headers["N"], "N"))
    k = _fraction(headers["K"], "K")
    budget = _fraction(headers["BUDGET"], "BUDGET")

    if m < 2:
        raise InstanceFormatError(f"M >= 2 olmali (makale: 2 <= M <= n): {m}")
    if n_total < 1:
        raise InstanceFormatError(f"N >= 1 olmali: {n_total}")
    if k <= 0:
        raise InstanceFormatError(f"K > 0 olmali: {k}")
    if budget <= 0:
        raise InstanceFormatError(f"BUDGET > 0 olmali: {budget}")
    if sorted(types) != list(range(1, m + 1)):
        raise InstanceFormatError(
            f"TYPE satirlari 1..{m} olmali; gelen: {sorted(types)}")

    weights, costs, rels = [], [], []
    for j in range(1, m + 1):
        w, c, p = types[j]
        if w <= 0:
            raise InstanceFormatError(f"TYPE {j}: agirlik > 0 olmali: {w}")
        if c < 0:
            raise InstanceFormatError(f"TYPE {j}: maliyet >= 0 olmali: {c}")
        if not (0 <= p <= 1):
            raise InstanceFormatError(
                f"TYPE {j}: guvenilirlik [0,1] disinda: {p}")
        weights.append(w)
        costs.append(c)
        rels.append(p)

    return Instance(
        name=headers["NAME"], m=m, n_total=n_total, k=k, budget=budget,
        weights=tuple(weights), costs=tuple(costs),
        reliabilities=tuple(rels),
    )
