"""sense'e göre fitness -> combined_score dönüşümü.

OpenEvolve daima MAKSİMİZE eder. Problemin yönü (SENSE) burada, tek yerde
combined_score işaretine çevrilir:

    min problem -> combined_score = -fitness
    max problem -> combined_score = +fitness

Bu dönüşümdeki bir işaret hatası evrimi sessizce tersine çevirir; bu yüzden
sense yalnızca tam olarak "min" veya "max" kabul edilir — yazım/büyük harf
hatası ValueError ile anında patlar.
"""

VALID_SENSES = ("min", "max")


def combined_score(fitness: float, sense: str) -> float:
    if sense not in VALID_SENSES:
        raise ValueError(
            f"sense {sense!r} geçersiz; yalnızca {VALID_SENSES} kabul edilir"
        )
    return -fitness if sense == "min" else fitness
