"""Instance parser: .cap dosyasi -> Instance. Bozuk dosya RAISE eder.

(Cozum tarafinin aksine instance tarafinda hata sert olmalidir: bozuk
instance ile kosulan her sey coptur — sessizce devam edilmez. Kofn io.py
deseni.) Capset instance'i minimal: yalnizca dimension.

    # yorum serbest
    dimension <n>
"""

from dataclasses import dataclass
from pathlib import Path


class InstanceFormatError(Exception):
    """Instance dosyasi format sozlesmesini (spec.py) saglamiyor."""


@dataclass(frozen=True)
class Instance:
    name: str
    dimension: int  # n; F_3^n uzayinin boyutu


def parse_instance(path) -> Instance:
    text = Path(path).read_text(encoding="utf-8")
    dimension = None
    name = Path(path).stem  # dosya adindan (capset-n8.cap -> capset-n8)

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        key = parts[0].lower()
        if key == "dimension":
            if len(parts) != 2:
                raise InstanceFormatError(
                    f"dimension tek deger ister: {raw!r}")
            try:
                dimension = int(parts[1])
            except ValueError:
                raise InstanceFormatError(
                    f"dimension tamsayi degil: {parts[1]!r}")
        else:
            raise InstanceFormatError(f"bilinmeyen satir: {raw!r}")

    if dimension is None:
        raise InstanceFormatError("zorunlu baslik eksik: dimension")

    if dimension < 1:
        raise InstanceFormatError(f"dimension >= 1 olmali: {dimension}")

    return Instance(name=name, dimension=dimension)
