"""Instance parser: .cover dosyasi -> Instance. Bozuk dosya RAISE eder.

(Cozum tarafinin aksine instance tarafinda hata sert olmalidir: bozuk
instance ile kosulan her sey coptur. kofn/capset io.py deseni.)

    # yorum serbest
    v <int>
    k <int>
    t <int>

Kisit: v > k > t >= 1.
"""

from dataclasses import dataclass
from pathlib import Path


class InstanceFormatError(Exception):
    """Instance dosyasi format sozlesmesini (spec.py) saglamiyor."""


@dataclass(frozen=True)
class Instance:
    name: str
    v: int  # evren buyuklugu
    k: int  # blok buyuklugu
    t: int  # kapsanacak altkume buyuklugu


_KEYS = ("v", "k", "t")


def parse_instance(path) -> Instance:
    text = Path(path).read_text(encoding="utf-8")
    vals = {}
    name = Path(path).stem

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        key = parts[0].lower()
        if key in _KEYS:
            if len(parts) != 2:
                raise InstanceFormatError(f"{key} tek deger ister: {raw!r}")
            if key in vals:
                raise InstanceFormatError(f"{key} iki kez tanimlanmis: {raw!r}")
            try:
                vals[key] = int(parts[1])
            except ValueError:
                raise InstanceFormatError(f"{key} tamsayi degil: {parts[1]!r}")
        else:
            raise InstanceFormatError(f"bilinmeyen satir: {raw!r}")

    missing = [key for key in _KEYS if key not in vals]
    if missing:
        raise InstanceFormatError(f"zorunlu baslik eksik: {', '.join(missing)}")

    v, k, t = vals["v"], vals["k"], vals["t"]
    if not (v > k > t >= 1):
        raise InstanceFormatError(
            f"v > k > t >= 1 olmali: v={v}, k={k}, t={t}")

    return Instance(name=name, v=v, k=k, t=t)
